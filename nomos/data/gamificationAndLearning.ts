/**
 * Should I App - Gamification, Learning, AI Coach, and System Management
 * Final feature set completing the 30+ features
 */

import { getDb } from "../db";
import { 
  resources,
  userAchievements,
  userChallenges,
  achievements,
  challenges,
  supportTickets,
  decisions,
  users
} from "../../drizzle/schema";
import { eq, desc, and, gte, sql } from "drizzle-orm";
import { invokeLLM } from "../_core/llm";

// ============================================================================
// LEARNING RESOURCES
// ============================================================================

export async function getResources(filters?: {
  category?: string;
  type?: string;
  searchQuery?: string;
}) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  let query = db.select().from(resources);
  
  const conditions = [];
  
  if (filters?.category) {
    conditions.push(eq(resources.category, filters.category));
  }
  
  if (filters?.type) {
    conditions.push(eq(resources.type, filters.type as any));
  }
  
  if (conditions.length > 0) {
    const results = await db.select().from(resources).where(and(...conditions)).orderBy(desc(resources.rating));
    if (filters?.searchQuery) {
      const searchLower = filters.searchQuery.toLowerCase();
      return results.filter(r => 
        r.title.toLowerCase().includes(searchLower) ||
        (r.description && r.description.toLowerCase().includes(searchLower))
      );
    }
    return results;
  }
  
  const results = await query.orderBy(desc(resources.rating));
  
  if (filters?.searchQuery) {
    const searchLower = filters.searchQuery.toLowerCase();
    return results.filter(r => 
      r.title.toLowerCase().includes(searchLower) ||
      (r.description && r.description.toLowerCase().includes(searchLower))
    );
  }
  
  return results;
}

export async function createResource(data: {
  title: string;
  description?: string;
  url?: string;
  content?: string;
  type: string;
  category: string;
  tags?: string[];
}) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  await db.insert(resources).values({
    title: data.title,
    description: data.description || null,
    url: data.url || null,
    content: data.content || null,
    type: data.type as any,
    category: data.category,
    tags: data.tags ? JSON.stringify(data.tags) : null,
    rating: 0,
    viewCount: 0
  });
  
  const [created] = await db.select()
    .from(resources)
    .where(eq(resources.title, data.title))
    .orderBy(desc(resources.createdAt))
    .limit(1);
  
  return created;
}

export async function incrementResourceViews(resourceId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const [resource] = await db.select()
    .from(resources)
    .where(eq(resources.id, resourceId));
  
  if (resource) {
    await db.update(resources)
      .set({ viewCount: resource.viewCount + 1 })
      .where(eq(resources.id, resourceId));
  }
}

// ============================================================================
// DECISION FRAMEWORKS
// ============================================================================

export interface DecisionFramework {
  name: string;
  description: string;
  steps: string[];
  useCases: string[];
  resources: string[];
}

export const DECISION_FRAMEWORKS: DecisionFramework[] = [
  {
    name: "WRAP Framework",
    description: "Widen options, Reality-test assumptions, Attain distance, Prepare to be wrong",
    steps: [
      "Widen your options - Consider more alternatives",
      "Reality-test your assumptions - Seek disconfirming evidence",
      "Attain distance before deciding - Take a 10/10/10 perspective",
      "Prepare to be wrong - Set tripwires and plan for failure"
    ],
    useCases: ["Career decisions", "Major life changes", "Business strategy"],
    resources: ["Decisive by Chip and Dan Heath"]
  },
  {
    name: "Eisenhower Matrix",
    description: "Prioritize decisions by urgency and importance",
    steps: [
      "Categorize as Urgent & Important (Do first)",
      "Important but Not Urgent (Schedule)",
      "Urgent but Not Important (Delegate)",
      "Neither Urgent nor Important (Eliminate)"
    ],
    useCases: ["Time management", "Task prioritization", "Daily decisions"],
    resources: ["The 7 Habits of Highly Effective People by Stephen Covey"]
  },
  {
    name: "Six Thinking Hats",
    description: "Examine decisions from six perspectives",
    steps: [
      "White Hat: Facts and information",
      "Red Hat: Emotions and intuition",
      "Black Hat: Risks and caution",
      "Yellow Hat: Benefits and optimism",
      "Green Hat: Creativity and alternatives",
      "Blue Hat: Process and control"
    ],
    useCases: ["Group decisions", "Complex problems", "Creative thinking"],
    resources: ["Six Thinking Hats by Edward de Bono"]
  },
  {
    name: "Cost-Benefit Analysis",
    description: "Quantify and compare costs vs benefits",
    steps: [
      "List all costs (financial, time, emotional)",
      "List all benefits (short-term and long-term)",
      "Assign monetary or weighted values",
      "Calculate net benefit",
      "Consider intangibles and risks"
    ],
    useCases: ["Financial decisions", "Business investments", "Major purchases"],
    resources: ["Economics textbooks", "Business analysis guides"]
  },
  {
    name: "Regret Minimization Framework",
    description: "Project yourself to age 80 and minimize future regret",
    steps: [
      "Imagine yourself at age 80",
      "Look back at this decision",
      "Ask: Will I regret not doing this?",
      "Choose the path with least regret"
    ],
    useCases: ["Career changes", "Life decisions", "Risk-taking"],
    resources: ["Jeff Bezos regret minimization framework"]
  }
];

export function getFramework(name: string): DecisionFramework | undefined {
  return DECISION_FRAMEWORKS.find(f => f.name === name);
}

export function getAllFrameworks(): DecisionFramework[] {
  return DECISION_FRAMEWORKS;
}

// ============================================================================
// CHARITY GUIDANCE (Islamic/Sadaqah context)
// ============================================================================

export async function getCharityGuidance(question: string): Promise<string> {
  const prompt = `Provide Islamic guidance on this charity/sadaqah decision:

**Question**: ${question}

Consider:
1. Islamic principles of charity (Zakat, Sadaqah, Waqf)
2. Intentions (Niyyah) and sincerity
3. Priority of recipients (family, neighbors, community)
4. Sustainable vs immediate impact
5. Quranic and Hadith references

Provide compassionate, practical guidance grounded in Islamic teachings.`;

  const response = await invokeLLM({
    messages: [
      { role: "system", content: "You are a knowledgeable Islamic scholar providing guidance on charity and good deeds." },
      { role: "user", content: prompt }
    ]
  });

  const content = response.choices[0].message.content;
  return typeof content === 'string' ? content : "Unable to provide guidance at this time.";
}

// ============================================================================
// GAMIFICATION - XP & LEVELS
// ============================================================================

export interface UserLevel {
  level: number;
  xp: number;
  xpForNextLevel: number;
  title: string;
}

const LEVEL_TITLES = [
  "Novice Decision Maker",
  "Thoughtful Chooser",
  "Strategic Thinker",
  "Wise Advisor",
  "Master Decision Maker",
  "Sage Counselor"
];

export function calculateLevel(totalXP: number): UserLevel {
  // XP required doubles each level: 100, 200, 400, 800, 1600, 3200...
  let level = 1;
  let xpRequired = 100;
  let xpSoFar = 0;
  
  while (totalXP >= xpSoFar + xpRequired && level < 50) {
    xpSoFar += xpRequired;
    level++;
    xpRequired *= 2;
  }
  
  const xpInCurrentLevel = totalXP - xpSoFar;
  const titleIndex = Math.min(Math.floor(level / 10), LEVEL_TITLES.length - 1);
  
  return {
    level,
    xp: xpInCurrentLevel,
    xpForNextLevel: xpRequired,
    title: LEVEL_TITLES[titleIndex]
  };
}

export async function awardXP(userId: number, amount: number, reason: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  // XP tracking would need to be added to users table or separate table
  // For now, return mock data
  const currentXP = 0;
  const newXP = currentXP + amount;
  
  // XP update would go here if users table had xp field
  // await db.update(users).set({ xp: newXP }).where(eq(users.id, userId));
  
  // Check for level up
  const oldLevel = calculateLevel(currentXP).level;
  const newLevel = calculateLevel(newXP).level;
  
  if (newLevel > oldLevel) {
    // Award level-up achievement (would need achievement ID mapping)
    // await awardAchievement(userId, levelAchievementId);
  }
  
  return { newXP, levelUp: newLevel > oldLevel, newLevel };
}

// XP rewards for different actions
export const XP_REWARDS = {
  CREATE_DECISION: 10,
  COMPLETE_WIZARD: 25,
  ADD_OUTCOME: 15,
  SHARE_DECISION: 20,
  HELP_OTHERS: 30,
  DAILY_STREAK: 50,
  COMPLETE_CHALLENGE: 100
};

// ============================================================================
// ACHIEVEMENTS
// ============================================================================

export async function awardAchievement(userId: number, achievementId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  // Check if already awarded
  const existing = await db.select()
    .from(userAchievements)
    .where(and(
      eq(userAchievements.userId, userId),
      eq(userAchievements.achievementId, achievementId)
    ));
  
  if (existing.length > 0) return null;
  
  await db.insert(userAchievements).values({
    userId,
    achievementId
  });
  
  // Award XP for achievement
  await awardXP(userId, 50, `Achievement: ${achievementId}`);
  
  return { achievementId, unlockedAt: new Date() };
}

export async function getUserAchievements(userId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.select()
    .from(userAchievements)
    .where(eq(userAchievements.userId, userId))
    .orderBy(desc(userAchievements.unlockedAt));
}

export const ACHIEVEMENTS = [
  { id: "first_decision", name: "First Step", description: "Made your first decision", xp: 50 },
  { id: "decision_maker_10", name: "Decision Maker", description: "Made 10 decisions", xp: 100 },
  { id: "decision_maker_50", name: "Prolific Decider", description: "Made 50 decisions", xp: 250 },
  { id: "wizard_master", name: "Wizard Master", description: "Completed 5 decision wizards", xp: 150 },
  { id: "sharer", name: "Generous Sharer", description: "Shared 10 decisions", xp: 100 },
  { id: "streak_7", name: "Week Warrior", description: "7-day decision streak", xp: 200 },
  { id: "streak_30", name: "Monthly Master", description: "30-day decision streak", xp: 500 },
  { id: "helper", name: "Community Helper", description: "Helped 5 people with decisions", xp: 200 },
  { id: "level_5", name: "Rising Star", description: "Reached level 5", xp: 100 },
  { id: "level_10", name: "Expert Decider", description: "Reached level 10", xp: 250 }
];

// ============================================================================
// CHALLENGES
// ============================================================================

export async function getUserChallenges(userId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.select()
    .from(userChallenges)
    .where(eq(userChallenges.userId, userId));
}

export async function startChallenge(userId: number, challengeId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  await db.insert(userChallenges).values({
    userId,
    challengeId,
    progress: 0,
    completed: 0,
    completedAt: null
  });
  
  const [created] = await db.select()
    .from(userChallenges)
    .where(and(
      eq(userChallenges.userId, userId),
      eq(userChallenges.challengeId, challengeId)
    ))
    .limit(1);
  
  return created;
}

export async function updateChallengeProgress(userId: number, challengeId: number, progress: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const [challenge] = await db.select()
    .from(userChallenges)
    .where(and(
      eq(userChallenges.userId, userId),
      eq(userChallenges.challengeId, challengeId),
      eq(userChallenges.completed, 0)
    ))
    .limit(1);
  
  if (!challenge) return null;
  
  const completed = progress >= 100 ? 1 : 0;
  
  await db.update(userChallenges)
    .set({ progress, completed })
    .where(eq(userChallenges.id, challenge.id));
  
  if (completed) {
    await awardXP(userId, XP_REWARDS.COMPLETE_CHALLENGE, `Challenge: ${challengeId}`);
  }
  
  return { progress, completed: completed === 1 };
}

// ============================================================================
// AI DECISION COACH
// ============================================================================

export interface CoachMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export async function chatWithCoach(
  userId: number,
  message: string,
  conversationHistory: CoachMessage[]
): Promise<string> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  // Get user's decision history for context
  const userDecisions = await db.select()
    .from(decisions)
    .where(eq(decisions.userId, userId))
    .orderBy(desc(decisions.createdAt))
    .limit(10);
  
  const decisionContext = userDecisions.length > 0
    ? `\n\nUser's recent decisions:\n${userDecisions.map(d => `- ${d.question} (${d.category})`).join('\n')}`
    : "";
  
  const systemPrompt = `You are an AI decision coach helping users make better decisions. 

Your role:
1. Ask clarifying questions to understand the decision
2. Help users explore options and perspectives
3. Identify biases and blind spots
4. Suggest decision frameworks when appropriate
5. Provide encouragement and support

Be conversational, empathetic, and insightful.${decisionContext}`;

  const messages = [
    { role: "system" as const, content: systemPrompt },
    ...conversationHistory.map(m => ({ role: m.role, content: m.content })),
    { role: "user" as const, content: message }
  ];

  const response = await invokeLLM({ messages });

  const content = response.choices[0].message.content;
  return typeof content === 'string' ? content : "I'm here to help. Can you tell me more about your decision?";
}

// ============================================================================
// ANALYTICS
// ============================================================================

export interface UserAnalytics {
  totalDecisions: number;
  decisionsThisWeek: number;
  decisionsThisMonth: number;
  averageConfidence: number;
  mostCommonCategory: string;
  completionRate: number;
  shareRate: number;
  level: UserLevel;
  achievements: number;
  streak: number;
}

export async function getUserAnalytics(userId: number): Promise<UserAnalytics> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  // User XP would be fetched here
  // const [user] = await db.select().from(users).where(eq(users.id, userId));
  // if (!user) throw new Error("User not found");
  
  const userDecisions = await db.select()
    .from(decisions)
    .where(eq(decisions.userId, userId));
  
  const now = new Date();
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const oneMonthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  
  const decisionsThisWeek = userDecisions.filter(d => d.createdAt >= oneWeekAgo).length;
  const decisionsThisMonth = userDecisions.filter(d => d.createdAt >= oneMonthAgo).length;
  
  const confidenceScores = userDecisions
    .filter(d => d.confidenceScore !== null)
    .map(d => d.confidenceScore!);
  const averageConfidence = confidenceScores.length > 0
    ? confidenceScores.reduce((a, b) => a + b, 0) / confidenceScores.length
    : 0;
  
  const categoryCount: Record<string, number> = {};
  userDecisions.forEach(d => {
    categoryCount[d.category] = (categoryCount[d.category] || 0) + 1;
  });
  const mostCommonCategory = Object.entries(categoryCount)
    .sort((a, b) => b[1] - a[1])[0]?.[0] || "none";
  
  const completedDecisions = userDecisions.filter(d => d.status === "completed").length;
  const completionRate = userDecisions.length > 0 ? completedDecisions / userDecisions.length : 0;
  
  const sharedDecisions = userDecisions.filter(d => d.shared === 1).length;
  const shareRate = userDecisions.length > 0 ? sharedDecisions / userDecisions.length : 0;
  
  const userAchievementsCount = await db.select()
    .from(userAchievements)
    .where(eq(userAchievements.userId, userId));
  
  return {
    totalDecisions: userDecisions.length,
    decisionsThisWeek,
    decisionsThisMonth,
    averageConfidence,
    mostCommonCategory,
    completionRate,
    shareRate,
    level: calculateLevel(0), // Would use user.xp if available
    achievements: userAchievementsCount.length,
    streak: 0 // TODO: Calculate from userProgress table
  };
}

// ============================================================================
// SUPPORT TICKETS
// ============================================================================

export async function createSupportTicket(data: {
  userId: number;
  subject: string;
  message: string;
  priority: string;
}) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  await db.insert(supportTickets).values({
    userId: data.userId,
    subject: data.subject,
    message: data.message,
    priority: data.priority as any,
    status: "open",
    assignedTo: null,
    resolution: null
  });
  
  const [created] = await db.select()
    .from(supportTickets)
    .where(eq(supportTickets.userId, data.userId))
    .orderBy(desc(supportTickets.createdAt))
    .limit(1);
  
  return created;
}

export async function getUserSupportTickets(userId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.select()
    .from(supportTickets)
    .where(eq(supportTickets.userId, userId))
    .orderBy(desc(supportTickets.createdAt));
}

export async function updateSupportTicket(
  ticketId: number,
  updates: {
    status?: string;
    resolution?: string;
    assignedTo?: number;
  }
) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  await db.update(supportTickets)
    .set(updates as any)
    .where(eq(supportTickets.id, ticketId));
  
  const [updated] = await db.select()
    .from(supportTickets)
    .where(eq(supportTickets.id, ticketId));
  
  return updated;
}
