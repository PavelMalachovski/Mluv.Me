"use client";

/**
 * Improved Onboarding Flow
 *
 * Multi-step wizard with:
 * - Czech level selection
 * - Conversation style selection
 * - Ready to start screen
 *
 * Native language is now configured in Settings.
 * Uses CS_TEXTS for Czech localization.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/lib/auth-store";
import CS_TEXTS from "@/lib/localization/cs";
import { ChevronRight, ChevronLeft, Loader2, Check } from "lucide-react";
import { cn } from "@/lib/utils";

type Step = "level" | "style" | "ready";

const STEPS: Step[] = ["level", "style", "ready"];

interface OnboardingProps {
    telegramId: number;
    firstName: string;
}

const LEVELS = [
    { code: "beginner", emoji: "🌱", label: CS_TEXTS.settings.levelBeginner, desc: "Základní fráze a slovíčka" },
    { code: "intermediate", emoji: "📚", label: CS_TEXTS.settings.levelIntermediate, desc: "Běžná konverzace" },
    { code: "advanced", emoji: "🎯", label: CS_TEXTS.settings.levelAdvanced, desc: "Složitější témata" },
    { code: "native", emoji: "⭐", label: CS_TEXTS.settings.levelNative, desc: "Plynulá čeština" },
];

const STYLES = [
    { code: "friendly", emoji: "😊", label: CS_TEXTS.settings.styleFriendly, desc: CS_TEXTS.settings.styleFriendlyDesc },
    { code: "tutor", emoji: "👨‍🏫", label: CS_TEXTS.settings.styleTutor, desc: CS_TEXTS.settings.styleTutorDesc },
    { code: "casual", emoji: "🍺", label: CS_TEXTS.settings.styleCasual, desc: CS_TEXTS.settings.styleCasualDesc },
];

export default function OnboardingPage() {
    const router = useRouter();
    const user = useAuthStore((state) => state.user);
    const updateUser = useAuthStore((state) => state.updateUser);

    const [currentStep, setCurrentStep] = useState<Step>("level");
    const [direction, setDirection] = useState<"forward" | "backward">("forward");
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form state — native language is now set in Settings, default to "ru"
    const nativeLanguage = user?.native_language || "ru";
    const [level, setLevel] = useState<string>("beginner");
    const [style, setStyle] = useState<string>("friendly");

    const currentIndex = STEPS.indexOf(currentStep);
    const progress = ((currentIndex + 1) / STEPS.length) * 100;

    const goNext = () => {
        if (currentIndex < STEPS.length - 1) {
            setDirection("forward");
            setCurrentStep(STEPS[currentIndex + 1]);
        }
    };

    const goBack = () => {
        if (currentIndex > 0) {
            setDirection("backward");
            setCurrentStep(STEPS[currentIndex - 1]);
        }
    };

    const handleComplete = async () => {
        if (!user) {
            router.push("/login");
            return;
        }

        setIsSubmitting(true);

        try {
            // Update user profile with selections
            const updatedUser = await apiClient.patch(`/api/v1/users/${user.id}`, {
                native_language: nativeLanguage,
                level: level,
            });

            // Update settings
            await apiClient.patch(`/api/v1/users/${user.id}/settings`, {
                conversation_style: style,
            });

            // Update local store
            updateUser(updatedUser);

            // Navigate to dashboard
            router.push("/dashboard");
        } catch (error) {
            console.error("Onboarding error:", error);
            // Still navigate to dashboard on error
            router.push("/dashboard");
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-purple-600 via-purple-500 to-indigo-600 flex flex-col">
            {/* Progress bar */}
            <div className="p-4">
                <div className="h-1.5 bg-white/30 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-white transition-all duration-500 ease-out rounded-full"
                        style={{ width: `${progress}%` }}
                    />
                </div>
                <div className="mt-2 text-center text-white/70 text-sm">
                    {currentIndex + 1} / {STEPS.length}
                </div>
            </div>

            {/* Step content */}
            <div className="flex-1 flex flex-col px-4 pb-4">
                <div
                    key={currentStep}
                    className={cn(
                        "flex-1 flex flex-col",
                        direction === "forward" ? "animate-slide-in-right" : "animate-slide-in-right"
                    )}
                >
                    {/* Level Step */}
                    {currentStep === "level" && (
                        <StepContainer
                            title={CS_TEXTS.onboarding.level.title}
                            subtitle={CS_TEXTS.onboarding.level.subtitle}
                        >
                            <div className="space-y-3">
                                {LEVELS.map((l) => (
                                    <OptionCard
                                        key={l.code}
                                        selected={level === l.code}
                                        onClick={() => setLevel(l.code)}
                                        horizontal
                                    >
                                        <span className="text-2xl mr-3">{l.emoji}</span>
                                        <div className="flex-1 text-left">
                                            <div className="font-medium">{l.label}</div>
                                            <div className="text-sm text-gray-500">{l.desc}</div>
                                        </div>
                                        {level === l.code && <Check className="h-5 w-5 text-purple-600" />}
                                    </OptionCard>
                                ))}
                            </div>
                        </StepContainer>
                    )}

                    {/* Style Step */}
                    {currentStep === "style" && (
                        <StepContainer
                            title={CS_TEXTS.onboarding.style.title}
                            subtitle={CS_TEXTS.onboarding.style.subtitle}
                        >
                            <div className="space-y-3">
                                {STYLES.map((s) => (
                                    <OptionCard
                                        key={s.code}
                                        selected={style === s.code}
                                        onClick={() => setStyle(s.code)}
                                        horizontal
                                    >
                                        <span className="text-2xl mr-3">{s.emoji}</span>
                                        <div className="flex-1 text-left">
                                            <div className="font-medium">{s.label}</div>
                                            <div className="text-sm text-gray-500">{s.desc}</div>
                                        </div>
                                        {style === s.code && <Check className="h-5 w-5 text-purple-600" />}
                                    </OptionCard>
                                ))}
                            </div>
                        </StepContainer>
                    )}

                    {/* Ready Step */}
                    {currentStep === "ready" && (
                        <StepContainer
                            title={CS_TEXTS.onboarding.ready.title}
                            subtitle={CS_TEXTS.onboarding.ready.subtitle}
                        >
                            <div className="text-center space-y-6">
                                {/* Mascot */}
                                <div className="text-8xl animate-bounce">📚</div>

                                {/* Summary */}
                                <div className="bg-white/10 rounded-xl p-4 space-y-2 text-white">
                                    <div className="flex justify-between">
                                        <span className="opacity-70">{CS_TEXTS.settings.levelSection}:</span>
                                        <span className="font-medium">
                                            {LEVELS.find((l) => l.code === level)?.emoji}{" "}
                                            {LEVELS.find((l) => l.code === level)?.label}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="opacity-70">{CS_TEXTS.settings.styleSection}:</span>
                                        <span className="font-medium">
                                            {STYLES.find((s) => s.code === style)?.emoji}{" "}
                                            {STYLES.find((s) => s.code === style)?.label}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </StepContainer>
                    )}
                </div>

                {/* Navigation buttons */}
                <div className="flex gap-3 mt-4">
                    {currentIndex > 0 && (
                        <button
                            onClick={goBack}
                            className="flex-1 py-3 px-6 bg-white/20 text-white rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-white/30 transition-colors"
                        >
                            <ChevronLeft className="h-5 w-5" />
                            {CS_TEXTS.common.back}
                        </button>
                    )}

                    {currentStep !== "ready" ? (
                        <button
                            onClick={goNext}
                            className="flex-1 py-3 px-6 bg-white text-purple-600 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-gray-100 transition-colors"
                        >
                            {CS_TEXTS.onboarding.nextBtn}
                            <ChevronRight className="h-5 w-5" />
                        </button>
                    ) : (
                        <button
                            onClick={handleComplete}
                            disabled={isSubmitting}
                            className="flex-1 py-3 px-6 bg-green-500 text-white rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-green-600 transition-colors disabled:opacity-50"
                        >
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                    Načítání...
                                </>
                            ) : (
                                <>
                                    {CS_TEXTS.onboarding.startBtn}
                                </>
                            )}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}

// Step container component
function StepContainer({
    title,
    subtitle,
    children,
}: {
    title: string;
    subtitle: string;
    children: React.ReactNode;
}) {
    return (
        <>
            <div className="text-center mb-6 text-white">
                <h1 className="text-2xl font-bold mb-2">{title}</h1>
                <p className="opacity-80">{subtitle}</p>
            </div>
            <div className="flex-1 bg-white rounded-2xl p-4 shadow-xl overflow-y-auto">
                {children}
            </div>
        </>
    );
}

// Option card component
function OptionCard({
    selected,
    onClick,
    horizontal = false,
    children,
}: {
    selected: boolean;
    onClick: () => void;
    horizontal?: boolean;
    children: React.ReactNode;
}) {
    return (
        <button
            onClick={onClick}
            className={cn(
                "w-full rounded-xl border-2 p-4 transition-all",
                horizontal ? "flex items-center" : "flex flex-col items-center",
                selected
                    ? "border-purple-500 bg-purple-50"
                    : "border-gray-200 hover:border-purple-300"
            )}
        >
            {children}
        </button>
    );
}
