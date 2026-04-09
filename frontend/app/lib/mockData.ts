// Mock data for prototype
export const mockActivities = [
  {
    id: "1",
    child: "Emma",
    type: "food",
    description: "Breakfast: Oatmeal with berries",
    time: "08:00 AM",
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
  },
  {
    id: "2",
    child: "Liam",
    type: "mood",
    description: "Happy & energetic",
    time: "09:30 AM",
    timestamp: new Date(Date.now() - 2.5 * 60 * 60 * 1000),
  },
  {
    id: "3",
    child: "Emma",
    type: "play",
    description: "Playtime at park",
    time: "10:15 AM",
    timestamp: new Date(Date.now() - 1.5 * 60 * 60 * 1000),
  },
  {
    id: "4",
    child: "Liam",
    type: "food",
    description: "Snack: Apple and peanut butter",
    time: "02:00 PM",
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
  },
];

export const mockReminders = [
  {
    id: "r1",
    title: "Emma's soccer practice",
    time: "04:00 PM",
    type: "calendar",
  },
  {
    id: "r2",
    title: "Give Liam afternoon snack",
    time: "03:30 PM",
    type: "recurring",
  },
  {
    id: "r3",
    title: "Grocery shopping - Pick up milk",
    time: "05:00 PM",
    type: "grocery",
  },
];

export const mockGroceryItems = [
  { id: "g1", name: "Milk", store: "Whole Foods", completed: false },
  { id: "g2", name: "Eggs", store: "Whole Foods", completed: false },
  { id: "g3", name: "Bread", store: "Whole Foods", completed: false },
  { id: "g4", name: "Chicken breast", store: "Costco", completed: false },
  { id: "g5", name: "Rice", store: "Costco", completed: false },
];

export const activityIcons: Record<string, string> = {
  food: "🍽️",
  mood: "😊",
  play: "🎮",
  sleep: "😴",
  other: "📝",
};
