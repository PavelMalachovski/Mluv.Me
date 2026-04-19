# Taxikar persona design

## Problem

Mluv.Me currently centers on a single Czech-speaking character, Honzik. The product needs a second selectable persona, **Taxikar**, who speaks in a rough taxi-driver style: candid, profane, sincere, and still helpful for Czech practice. The new persona must work in both text and voice, be available to all users at launch, and reuse the existing learning and conversation systems instead of creating a parallel feature stack.

## Goals

- Add Taxikar as a selectable persona in the app and bot.
- Keep one shared conversation, correction, stats, and subscription core.
- Support both text and voice responses for Taxikar from day one.
- Preserve a clear tone boundary: rough and profane, but never hateful, slur-based, threatening, or targeted.
- Keep persona behavior stable across sessions by persisting the user selection.

## Non-goals

- Building a general admin UI for creating arbitrary personas.
- Reworking pricing or subscription entitlements for persona access.
- Redesigning the broader learning loop, streaks, stars, or saved-word features.

## Proposed approach

Introduce a **persona layer on top of the shared conversation core**. Honzik and Taxikar remain different configurations of the same product flow rather than separate systems. Each persona supplies its own identity and generation settings, while all shared features remain implemented once.

This is preferred over hard-coded branching because it keeps the codebase maintainable as persona-specific behavior grows. It is also intentionally narrower than a fully data-driven persona platform, which would add unnecessary complexity for a two-character product.

## Architecture

### Shared core

The existing backend conversation flow remains the source of truth for:

- speech-to-text and text intake
- correction/explanation logic
- dialogue generation orchestration
- progress tracking, stats, streaks, and stars
- subscription and account checks

### Persona layer

Add a persona abstraction that the backend, frontend, and bot all reference. Each persona definition should include:

- `id`
- display name
- short localized description
- prompt template or prompt fragment
- tone rules and moderation constraints
- voice configuration
- visual metadata for pickers and labels

Initial personas:

- `honzik`
- `taxikar`

Taxikar is implemented as a first-class persona beside Honzik, not as a special-case feature flag.

## UX and component changes

### Frontend

Add a simple persona picker that lets users choose between Honzik and Taxikar. The picker should show a short preview of each character so users understand the difference before switching. The selected persona should be saved in user-facing settings or profile-backed state so the choice persists.

### Bot

Expose the same choice in the Telegram bot using the existing interaction style for user settings. The bot should present persona names and short descriptions, then persist the chosen value so future chat turns continue with the same character.

### Backend

Accept a `persona_id` with relevant chat or response-generation requests. For persisted conversations, the backend should resolve the effective persona from stored user/chat settings when the client does not send it explicitly. Unsupported persona IDs must fail validation clearly instead of silently defaulting.

## Data flow

1. User selects Taxikar in the app or bot.
2. The client stores or submits `persona_id=taxikar`.
3. The backend resolves the Taxikar persona definition.
4. The shared conversation pipeline assembles prompt context using common learner state plus Taxikar-specific instructions.
5. The response generator produces text in Taxikar's tone.
6. If the response is voiced, TTS uses Taxikar's configured voice settings.
7. Shared downstream systems persist the conversation and update progress exactly as they do for Honzik.

## Taxikar behavior contract

Taxikar should feel like a blunt but warm Czech taxi driver helping the learner speak more naturally about life. The persona is allowed to use profanity and colloquial language, but it must not:

- use slurs
- threaten the user
- degrade into hateful or targeted abuse
- stop being educational or helpful

Taxikar should still:

- explain Czech naturally
- correct mistakes clearly
- keep the conversation moving
- sound sincere rather than cruel

## Safety and moderation behavior

The system should preserve the Taxikar identity without letting unsafe output through.

- Prompt rules for Taxikar must explicitly encode the allowed tone and the disallowed categories above.
- If a draft output violates the persona boundary, the backend should retry generation with the same persona and stronger moderation instructions.
- If repeated retries fail, the backend should return a toned-down Taxikar response that stays colloquial and sincere rather than switching to Honzik.
- Moderation-related failures should be observable through existing logging patterns so the team can inspect prompt quality and model behavior.

## Error handling

- Unknown `persona_id`: return a validation error.
- Missing stored persona: fall back to the existing default persona policy only when no explicit invalid value was provided.
- Voice generation failure for Taxikar: keep the Taxikar text response and use a neutral fallback voice only for that response if necessary.
- Persona config mismatch: fail loudly in backend validation rather than silently ignoring incomplete configuration.

## Testing strategy

### Backend tests

- persona resolution returns the correct configuration
- unsupported persona IDs produce validation errors
- prompt assembly differs between Honzik and Taxikar where expected
- moderation retry logic keeps Taxikar active instead of switching personas

### Frontend tests

- persona picker renders both characters
- selection changes the active persona
- selected persona persists across reloads or restored sessions
- outbound requests include the correct `persona_id`

### Bot tests

- settings flow exposes both personas
- selecting Taxikar persists correctly
- subsequent bot interactions use the selected persona

### Integration tests

- Honzik and Taxikar follow the same conversation pipeline
- persona-specific prompt payloads and voice settings differ correctly
- shared learning systems keep working regardless of selected persona

## Rollout notes

- Launch Taxikar for all users.
- Keep the implementation narrow: two curated personas, one shared core.
- Write the implementation plan around backend persona abstraction first, then frontend/bot selection surfaces, then tests and prompt tuning.
