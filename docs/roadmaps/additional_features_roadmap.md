# Additional Features & AI/ML Roadmap

**Project:** Mluv.Me
**Last Updated:** December 7, 2025
**Status:** Ready for Implementation
**Expected Timeline:** 10-14 weeks
**Priority:** MEDIUM

---

## 📊 Executive Summary

This roadmap covers advanced AI/ML enhancements and UX boosters beyond the core roadmap: fine-tuning, pronunciation scoring, onboarding, gamification, content packs, and community features.

---

## 🎯 Objectives & Metrics
- Improve correction quality (target +10 correctness points for A1-B1)
- Increase weekly retention by 10-15%
- Grow paid conversion via premium content (+5%)
- Enable marketplace-ready content primitives

---

## 🤖 Phase 1: AI/ML Enhancements (4-6 weeks)

### 1.1 Fine-Tuned Model for Czech
- Collect high-quality pairs (user input → ideal Honzík response).
- Anonymize data; filter toxicity; balance levels.
- Fine-tune GPT-4o or smaller model; A/B test vs base.

**Success:** 10-15% reduction in correction errors for beginner content.

### 1.2 Pronunciation Scoring
- Prototype with wav2vec2 (Czech fine-tune) for phoneme-level scoring.
- Output overall score + per-phoneme feedback (e.g., r/ř issues).
- Ship as Expert-tier feature.

**Success:** Meaningful, consistent scores; <5% disagreement with human raters on sample set.

### 1.3 Smart Context Management
- Summarize long histories with GPT-3.5; keep last 3 full messages.
- Target 30-40% token savings with no quality drop.

**Success:** OpenAI cost per user reduced 20%+ on long sessions.

---

## 🧭 Phase 2: Onboarding & Personalization (2-3 weeks)

### 2.1 Adaptive Onboarding
- Multi-step flow: intro → level assessment (30s audio) → goals → topics.
- Auto-set czech_level and focus areas; allow user confirmation.

### 2.2 Weekly Insights
- Generate weekly progress summaries via OpenAI using stats + proficiency.
- Deliver via Telegram and email; include actionable tips.

### 2.3 Learning Style Signals
- Extend settings: learning_style, preferred_topics, focus_areas, challenge_difficulty.
- Feed into Honzík prompt and exercise generation.

**Success:** +10% D7 retention for new cohorts.

---

## 🏅 Phase 3: Gamification & Content (3-4 weeks)

### 3.1 Achievements & Leaderboards
- Achievement system with badges; unlock events on streaks, scores, consistency.
- Weekly/monthly leaderboards (stars, streaks, improvement).

### 3.2 Themed Lesson Packs
- Data model for lesson packs (theme, difficulty, premium flag).
- Authoring flow for internal team; later marketplace use.
- Offer paid packs (micropayments) for non-subscription upsell.

### 3.3 Social Sharing
- Generate shareable images for achievements (PIL-based); share to Telegram Stories/others.

**Success:** +5% virality; incremental revenue from packs.

---

## 🌐 Phase 4: Community & Marketplace Foundations (1-2 weeks)

### 4.1 Community Spaces
- Lightweight Discord/Forum integration link from bot/web.
- Content guidelines and moderation hooks.

### 4.2 Tutor Marketplace Prep
- Reuse lesson pack model for tutor-created content.
- Profiles: languages, specializations, rates, verification status.
- Booking primitives align with monetization roadmap.

**Success:** Readiness for marketplace launch; initial tutor beta list.

---

## ✅ Testing & Rollout
- A/B tests for fine-tune vs base; monitor correction quality, cost, retention.
- Human eval set for pronunciation and corrections.
- Feature flags for onboarding, insights, achievements.
- Gradual rollout per cohort/region; monitor retention and conversion.

---

## 📚 References
- OpenAI fine-tuning: https://platform.openai.com/docs/guides/fine-tuning
- Hugging Face wav2vec2: https://huggingface.co/models
- Gamification patterns: Duolingo approach

---

**Next Steps:** Approve scope, set up data pipelines for fine-tune, create evaluation sets, implement phased feature flags.
