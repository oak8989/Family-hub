from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.schemas import Recipe
from auth import get_current_user
from database import db
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import json
import re
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("", response_model=List[Recipe])
async def get_recipes(user: dict = Depends(get_current_user)):
    recipes = await db.recipes.find({"family_id": user["family_id"]}, {"_id": 0}).to_list(1000)
    for r in recipes:
        r.pop("family_id", None)
    return recipes


@router.post("", response_model=Recipe)
async def create_recipe(recipe: Recipe, user: dict = Depends(get_current_user)):
    recipe_doc = recipe.model_dump()
    recipe_doc["family_id"] = user["family_id"]
    recipe_doc["created_by"] = user["user_id"]
    await db.recipes.insert_one(recipe_doc)
    del recipe_doc["_id"]
    del recipe_doc["family_id"]
    return recipe_doc


@router.get("/{recipe_id}")
async def get_recipe(recipe_id: str, user: dict = Depends(get_current_user)):
    recipe = await db.recipes.find_one({"id": recipe_id, "family_id": user["family_id"]}, {"_id": 0})
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/{recipe_id}")
async def update_recipe(recipe_id: str, recipe: Recipe, user: dict = Depends(get_current_user)):
    recipe_doc = recipe.model_dump()
    await db.recipes.update_one({"id": recipe_id, "family_id": user["family_id"]}, {"$set": recipe_doc})
    return recipe_doc


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: str, user: dict = Depends(get_current_user)):
    await db.recipes.delete_one({"id": recipe_id, "family_id": user["family_id"]})
    return {"message": "Recipe deleted"}



class ImportURLRequest(BaseModel):
    url: str


def extract_json_ld_recipe(soup):
    """Extract recipe from JSON-LD structured data (Schema.org)."""
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'Recipe':
                        return item
            elif isinstance(data, dict):
                if data.get('@type') == 'Recipe':
                    return data
                if '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') == 'Recipe':
                            return item
        except (json.JSONDecodeError, TypeError):
            continue
    return None


def clean_instruction(text):
    """Clean instruction text."""
    text = re.sub(r'<[^>]+>', '', str(text))
    text = text.strip()
    return text if text else None


def parse_recipe_data(json_ld):
    """Parse JSON-LD recipe into our format."""
    name = json_ld.get('name', 'Imported Recipe')

    # Ingredients
    ingredients = json_ld.get('recipeIngredient', [])
    if not isinstance(ingredients, list):
        ingredients = [str(ingredients)]

    # Instructions
    raw_instructions = json_ld.get('recipeInstructions', [])
    instructions = []
    if isinstance(raw_instructions, list):
        for step in raw_instructions:
            if isinstance(step, str):
                cleaned = clean_instruction(step)
                if cleaned:
                    instructions.append(cleaned)
            elif isinstance(step, dict):
                text = step.get('text', step.get('name', ''))
                cleaned = clean_instruction(text)
                if cleaned:
                    instructions.append(cleaned)
    elif isinstance(raw_instructions, str):
        for line in raw_instructions.split('\n'):
            cleaned = clean_instruction(line)
            if cleaned:
                instructions.append(cleaned)

    # Times
    def parse_duration(dur):
        if not dur:
            return ''
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', str(dur))
        if match:
            h, m = match.group(1), match.group(2)
            parts = []
            if h:
                parts.append(f"{h}h")
            if m:
                parts.append(f"{m}m")
            return ' '.join(parts) if parts else ''
        return str(dur).replace('PT', '').replace('H', 'h ').replace('M', 'm').strip()

    prep_time = parse_duration(json_ld.get('prepTime', ''))
    cook_time = parse_duration(json_ld.get('cookTime', ''))

    # Servings
    servings = 4
    yield_val = json_ld.get('recipeYield', '')
    if isinstance(yield_val, list):
        yield_val = yield_val[0] if yield_val else ''
    match = re.search(r'(\d+)', str(yield_val))
    if match:
        servings = int(match.group(1))

    # Category
    category = json_ld.get('recipeCategory', 'Main Course')
    if isinstance(category, list):
        category = category[0] if category else 'Main Course'

    # Image
    image = json_ld.get('image', '')
    if isinstance(image, list):
        image = image[0] if image else ''
    elif isinstance(image, dict):
        image = image.get('url', '')

    return {
        'name': name,
        'description': json_ld.get('description', ''),
        'ingredients': ingredients,
        'instructions': instructions,
        'prep_time': prep_time,
        'cook_time': cook_time,
        'servings': servings,
        'category': category,
        'image_url': image,
    }


def fallback_scrape(soup, url):
    """Fallback: try to extract recipe info from HTML content."""
    title = ''
    if soup.title:
        title = soup.title.string or ''
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text(strip=True)

    description = ''
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        description = meta_desc.get('content', '')

    image = ''
    og_image = soup.find('meta', property='og:image')
    if og_image:
        image = og_image.get('content', '')

    return {
        'name': title or 'Imported Recipe',
        'description': description,
        'ingredients': [],
        'instructions': [],
        'prep_time': '',
        'cook_time': '',
        'servings': 4,
        'category': 'Main Course',
        'image_url': image,
    }


@router.post("/import-url")
async def import_recipe_from_url(req: ImportURLRequest, user: dict = Depends(get_current_user)):
    url = req.url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")

    soup = BeautifulSoup(response.text, 'lxml')
    json_ld = extract_json_ld_recipe(soup)

    if json_ld:
        recipe_data = parse_recipe_data(json_ld)
    else:
        recipe_data = fallback_scrape(soup, url)

    recipe_data['source_url'] = url
    return recipe_data
