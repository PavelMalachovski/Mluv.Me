"use client"

import { useState } from "react"
import { Beer, Train, ShoppingCart, Stethoscope, Briefcase, MessageSquare, Utensils, MapPin } from "lucide-react"

interface Topic {
    id: string
    name: string
    nameCzech: string
    description: string
    icon: React.ReactNode
    color: string
}

const TOPICS: Topic[] = [
    {
        id: "hospoda",
        name: "At the Pub",
        nameCzech: "V hospodě",
        description: "Order drinks, chat with locals",
        icon: <Beer className="h-6 w-6" />,
        color: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    },
    {
        id: "nadrazi",
        name: "Train Station",
        nameCzech: "Na nádraží",
        description: "Buy tickets, ask for directions",
        icon: <Train className="h-6 w-6" />,
        color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    },
    {
        id: "obchod",
        name: "At the Store",
        nameCzech: "V obchodě",
        description: "Shopping, prices, paying",
        icon: <ShoppingCart className="h-6 w-6" />,
        color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    },
    {
        id: "lekar",
        name: "At the Doctor",
        nameCzech: "U lékaře",
        description: "Health, symptoms, pharmacy",
        icon: <Stethoscope className="h-6 w-6" />,
        color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    },
    {
        id: "prace",
        name: "At Work",
        nameCzech: "V práci",
        description: "Office, meetings, colleagues",
        icon: <Briefcase className="h-6 w-6" />,
        color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
    },
    {
        id: "restaurace",
        name: "Restaurant",
        nameCzech: "V restauraci",
        description: "Ordering food, reservations",
        icon: <Utensils className="h-6 w-6" />,
        color: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
    },
    {
        id: "turistika",
        name: "Tourism",
        nameCzech: "Turistika",
        description: "Sightseeing, directions, attractions",
        icon: <MapPin className="h-6 w-6" />,
        color: "bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400",
    },
    {
        id: "free",
        name: "Free Conversation",
        nameCzech: "Volná konverzace",
        description: "Talk about anything!",
        icon: <MessageSquare className="h-6 w-6" />,
        color: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400",
    },
]

interface TopicSelectorProps {
    selectedTopic: string | null
    onSelectTopic: (topic: string | null) => void
}

export function TopicSelector({ selectedTopic, onSelectTopic }: TopicSelectorProps) {
    return (
        <div className="space-y-4">
            <div className="text-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-1">
                    Choose a Topic
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                    Select a conversation theme or go with free conversation
                </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
                {TOPICS.map((topic) => (
                    <button
                        key={topic.id}
                        onClick={() => onSelectTopic(topic.id === selectedTopic ? null : topic.id)}
                        className={`p-4 rounded-xl text-left transition-all ${selectedTopic === topic.id
                                ? "ring-2 ring-primary ring-offset-2 dark:ring-offset-gray-900"
                                : ""
                            } ${topic.color}`}
                    >
                        <div className="flex items-start gap-3">
                            <div className="mt-0.5">{topic.icon}</div>
                            <div className="flex-1 min-w-0">
                                <div className="font-medium text-sm truncate">{topic.nameCzech}</div>
                                <div className="text-xs opacity-75 truncate">{topic.name}</div>
                            </div>
                        </div>
                    </button>
                ))}
            </div>

            {selectedTopic && (
                <div className="mt-4 p-3 rounded-lg bg-primary/10 text-sm text-center">
                    <span className="font-medium">Topic: </span>
                    {TOPICS.find(t => t.id === selectedTopic)?.nameCzech}
                    <span className="text-xs ml-2 text-gray-500">
                        ({TOPICS.find(t => t.id === selectedTopic)?.description})
                    </span>
                </div>
            )}
        </div>
    )
}

export { TOPICS }
export type { Topic }
