import React, { useState, useEffect } from 'react';
import { Lightbulb, ChefHat, ShoppingCart, Check, X, Sparkles, RefreshCw } from 'lucide-react';
import { suggestionsAPI, pantryAPI } from '../lib/api';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Link } from 'react-router-dom';

const SuggestionsPage = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [pantryItems, setPantryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [suggestionsRes, pantryRes] = await Promise.all([
        suggestionsAPI.getSuggestions(),
        pantryAPI.getItems()
      ]);
      setSuggestions(suggestionsRes.data);
      setPantryItems(pantryRes.data);
    } catch (error) {
      toast.error('Failed to load suggestions');
    }
    setLoading(false);
  };

  const loadAISuggestions = async () => {
    if (pantryItems.length === 0) {
      toast.error('Add items to your pantry first!');
      return;
    }
    setAiLoading(true);
    try {
      const response = await suggestionsAPI.getAISuggestions();
      if (response.data.suggestions) {
        setAiSuggestions(response.data.suggestions);
        toast.success('AI suggestions generated!');
      } else {
        toast.info(response.data.message || 'No AI suggestions available');
      }
    } catch (error) {
      toast.error('Failed to generate AI suggestions');
    }
    setAiLoading(false);
  };

  const getMatchColor = (percent) => {
    if (percent >= 80) return 'bg-green-500';
    if (percent >= 50) return 'bg-yellow-500';
    return 'bg-terracotta';
  };

  return (
    <div className="space-y-6" data-testid="suggestions-page">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-heading font-bold text-navy flex items-center gap-3">
            <Lightbulb className="w-8 h-8 text-cyan-500" />
            Meal Ideas
          </h1>
          <p className="text-navy-light mt-1">Recipes based on what's in your pantry</p>
        </div>
      </div>

      {/* Pantry summary */}
      <div className="card-cozy bg-cyan-50 border-cyan-200">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-cyan-100 rounded-xl flex items-center justify-center">
            <ChefHat className="w-6 h-6 text-cyan-600" />
          </div>
          <div className="flex-1">
            <h2 className="font-heading font-bold text-navy">Your Pantry</h2>
            <p className="text-sm text-navy-light">
              {pantryItems.length} items available for cooking
            </p>
          </div>
          <Link to="/pantry">
            <Button variant="outline" className="border-cyan-300 text-cyan-600 hover:bg-cyan-100">
              View Pantry
            </Button>
          </Link>
        </div>
      </div>

      {/* Suggestions */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="spinner" />
        </div>
      ) : suggestions.length === 0 ? (
        <div className="card-cozy text-center py-12">
          <Lightbulb className="w-16 h-16 text-sunny mx-auto mb-4" />
          <h3 className="text-xl font-heading font-bold text-navy mb-2">No suggestions yet</h3>
          <p className="text-navy-light font-handwritten text-lg mb-4">
            Add recipes and pantry items to get personalized meal suggestions!
          </p>
          <div className="flex gap-3 justify-center">
            <Link to="/recipes">
              <Button className="btn-secondary">Add Recipes</Button>
            </Link>
            <Link to="/pantry">
              <Button className="btn-secondary">Add Pantry Items</Button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-navy-light">
            Found {suggestions.length} recipes you can make with your pantry items
          </p>
          
          {suggestions.map((suggestion, index) => (
            <div
              key={suggestion.recipe.id}
              className="card-cozy group"
              data-testid={`suggestion-${suggestion.recipe.id}`}
            >
              <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                {suggestion.recipe.image_url && (
                  <img
                    src={suggestion.recipe.image_url}
                    alt={suggestion.recipe.name}
                    className="w-full sm:w-32 h-32 object-cover rounded-2xl"
                  />
                )}
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <span className="text-xs text-cyan-600 font-medium">
                        #{index + 1} Best Match
                      </span>
                      <h3 className="font-heading font-bold text-navy text-xl">
                        {suggestion.recipe.name}
                      </h3>
                      {suggestion.recipe.description && (
                        <p className="text-sm text-navy-light mt-1 line-clamp-2">
                          {suggestion.recipe.description}
                        </p>
                      )}
                    </div>
                    
                    <div className="text-right">
                      <span className={`text-2xl font-heading font-bold ${
                        suggestion.match_percent >= 80 ? 'text-green-600' :
                        suggestion.match_percent >= 50 ? 'text-yellow-600' :
                        'text-terracotta'
                      }`}>
                        {suggestion.match_percent}%
                      </span>
                      <p className="text-xs text-navy-light">match</p>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm text-navy-light">
                        {suggestion.matches}/{suggestion.total_ingredients} ingredients
                      </span>
                      <Progress 
                        value={suggestion.match_percent} 
                        className="flex-1 h-2"
                      />
                    </div>
                    
                    {suggestion.missing.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs text-navy-light mb-2 flex items-center gap-1">
                          <ShoppingCart className="w-3 h-3" />
                          Missing ingredients:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {suggestion.missing.slice(0, 5).map((ing, i) => (
                            <span
                              key={i}
                              className="text-xs px-2 py-1 bg-red-50 text-red-600 rounded-full flex items-center gap-1"
                            >
                              <X className="w-3 h-3" />
                              {ing}
                            </span>
                          ))}
                          {suggestion.missing.length > 5 && (
                            <span className="text-xs text-navy-light">
                              +{suggestion.missing.length - 5} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {suggestion.matches > 0 && (
                      <div className="mt-3">
                        <p className="text-xs text-navy-light mb-2 flex items-center gap-1">
                          <Check className="w-3 h-3 text-green-500" />
                          You have:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {suggestion.recipe.ingredients
                            ?.filter(ing => !suggestion.missing.includes(ing.toLowerCase()))
                            .slice(0, 5)
                            .map((ing, i) => (
                              <span
                                key={i}
                                className="text-xs px-2 py-1 bg-green-50 text-green-600 rounded-full flex items-center gap-1"
                              >
                                <Check className="w-3 h-3" />
                                {ing}
                              </span>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-4 flex gap-3">
                    <Link to="/recipes">
                      <Button variant="ghost" className="text-terracotta hover:bg-terracotta/10">
                        View Recipe
                      </Button>
                    </Link>
                    <Link to="/meals">
                      <Button className="btn-secondary">
                        Add to Meal Plan
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* AI Suggestions Section */}
      <div className="card-cozy bg-gradient-to-r from-purple-50 to-cyan-50 border-purple-200">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-xl flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-heading font-bold text-navy">AI-Powered Meal Ideas</h3>
            <p className="text-sm text-navy-light">Get creative suggestions based on your pantry</p>
          </div>
          <Button 
            onClick={loadAISuggestions}
            disabled={aiLoading || pantryItems.length === 0}
            className="bg-gradient-to-r from-purple-500 to-cyan-500 text-white hover:opacity-90 w-full sm:w-auto"
            data-testid="generate-ai-btn"
          >
            {aiLoading ? (
              <span className="flex items-center gap-2"><RefreshCw className="w-4 h-4 animate-spin" />Thinking...</span>
            ) : (
              <span className="flex items-center gap-2"><Sparkles className="w-4 h-4" />Generate Ideas</span>
            )}
          </Button>
        </div>
        
        {aiSuggestions.length > 0 && (
          <div className="space-y-4 mt-4 pt-4 border-t border-purple-200">
            {aiSuggestions.map((meal, idx) => (
              <div key={idx} className="bg-white rounded-xl p-4 shadow-sm" data-testid={`ai-meal-${idx}`}>
                <h4 className="font-heading font-bold text-navy">{meal.name}</h4>
                <p className="text-sm text-navy-light mt-1">{meal.description}</p>
                {meal.ingredients && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {meal.ingredients.slice(0, 6).map((ing, i) => (
                      <span key={i} className={`text-xs px-2 py-0.5 rounded-full ${
                        ing.includes('(have)') ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                      }`}>{ing.replace('(have)', '').replace('(need)', '').trim()}</span>
                    ))}
                  </div>
                )}
                {meal.tips && (
                  <p className="text-xs text-purple-600 mt-2 italic">Tip: {meal.tips}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tips */}
      <div className="card-cozy bg-sunny/10 border-sunny/30">
        <h3 className="font-heading font-bold text-navy mb-3">💡 Tips for better suggestions</h3>
        <ul className="space-y-2 text-sm text-navy-light">
          <li>• Add more recipes to your Recipe Box</li>
          <li>• Keep your Pantry inventory up to date</li>
          <li>• Scan barcodes to quickly add items to your pantry</li>
          <li>• Include common ingredients in your recipes</li>
        </ul>
      </div>
    </div>
  );
};

export default SuggestionsPage;
