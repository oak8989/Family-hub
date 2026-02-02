import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  pinLogin: (pin) => api.post('/auth/pin-login', { pin }),
  getMe: () => api.get('/auth/me'),
};

// Family
export const familyAPI = {
  create: (data) => api.post('/family/create', data),
  get: () => api.get('/family'),
  getMembers: () => api.get('/family/members'),
  join: (familyId) => api.post(`/family/join/${familyId}`),
};

// Calendar
export const calendarAPI = {
  getEvents: () => api.get('/calendar'),
  createEvent: (data) => api.post('/calendar', data),
  updateEvent: (id, data) => api.put(`/calendar/${id}`, data),
  deleteEvent: (id) => api.delete(`/calendar/${id}`),
};

// Shopping List
export const shoppingAPI = {
  getItems: () => api.get('/shopping'),
  createItem: (data) => api.post('/shopping', data),
  updateItem: (id, data) => api.put(`/shopping/${id}`, data),
  deleteItem: (id) => api.delete(`/shopping/${id}`),
  clearChecked: () => api.delete('/shopping'),
};

// Tasks
export const tasksAPI = {
  getTasks: () => api.get('/tasks'),
  createTask: (data) => api.post('/tasks', data),
  updateTask: (id, data) => api.put(`/tasks/${id}`, data),
  deleteTask: (id) => api.delete(`/tasks/${id}`),
};

// Notes
export const notesAPI = {
  getNotes: () => api.get('/notes'),
  createNote: (data) => api.post('/notes', data),
  updateNote: (id, data) => api.put(`/notes/${id}`, data),
  deleteNote: (id) => api.delete(`/notes/${id}`),
};

// Messages
export const messagesAPI = {
  getMessages: () => api.get('/messages'),
  sendMessage: (data) => api.post('/messages', data),
};

// Budget
export const budgetAPI = {
  getEntries: () => api.get('/budget'),
  createEntry: (data) => api.post('/budget', data),
  updateEntry: (id, data) => api.put(`/budget/${id}`, data),
  deleteEntry: (id) => api.delete(`/budget/${id}`),
  getSummary: () => api.get('/budget/summary'),
};

// Meal Plans
export const mealPlanAPI = {
  getPlans: () => api.get('/meal-plans'),
  createPlan: (data) => api.post('/meal-plans', data),
  updatePlan: (id, data) => api.put(`/meal-plans/${id}`, data),
  deletePlan: (id) => api.delete(`/meal-plans/${id}`),
};

// Recipes
export const recipesAPI = {
  getRecipes: () => api.get('/recipes'),
  getRecipe: (id) => api.get(`/recipes/${id}`),
  createRecipe: (data) => api.post('/recipes', data),
  updateRecipe: (id, data) => api.put(`/recipes/${id}`, data),
  deleteRecipe: (id) => api.delete(`/recipes/${id}`),
};

// Grocery List
export const groceryAPI = {
  getItems: () => api.get('/grocery'),
  createItem: (data) => api.post('/grocery', data),
  updateItem: (id, data) => api.put(`/grocery/${id}`, data),
  deleteItem: (id) => api.delete(`/grocery/${id}`),
  clearChecked: () => api.delete('/grocery'),
};

// Contacts
export const contactsAPI = {
  getContacts: () => api.get('/contacts'),
  createContact: (data) => api.post('/contacts', data),
  updateContact: (id, data) => api.put(`/contacts/${id}`, data),
  deleteContact: (id) => api.delete(`/contacts/${id}`),
};

// Photos
export const photosAPI = {
  getPhotos: () => api.get('/photos'),
  uploadPhoto: (formData) => api.post('/photos', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getPhotoUrl: (id) => `${API_URL}/photos/${id}/file`,
  deletePhoto: (id) => api.delete(`/photos/${id}`),
};

// Pantry
export const pantryAPI = {
  getItems: () => api.get('/pantry'),
  createItem: (data) => api.post('/pantry', data),
  updateItem: (id, data) => api.put(`/pantry/${id}`, data),
  deleteItem: (id) => api.delete(`/pantry/${id}`),
  lookupBarcode: (barcode) => api.get(`/pantry/barcode/${barcode}`),
};

// Meal Suggestions
export const suggestionsAPI = {
  getSuggestions: () => api.get('/meal-suggestions'),
};

export default api;
