# WardLog — Frontend

The web client for WardLog. Three main areas: **Chat** (log activities by talking to the
assistant), **Timesheet** (view and manage logged activities, close months), and **Reports**
(charts over logged work), plus **Login/Register**.

---

## Working agreement (read first)

- Do only what I explicitly ask. Do not take initiative beyond the current instruction.
- Do not create, modify, or delete files, run commands, or refactor unless I ask for it.
- If something seems missing, wrong, or worth doing, **tell me and wait** — propose, don't act.
- Treat everything below as reference context, not a to-do list. It describes the intended
  design; it is not an instruction to build any of it on your own.
- When a request is ambiguous, ask before proceeding.

---

## Stack

- **React + Vite + TypeScript**
- **Tailwind CSS** — plain, no component library. We have our own design, so components are
  hand-built for full control.
- **Plain `fetch`** for data — no React Query for now. Loading/error state is handled with
  `useState`/`useEffect` in components or small custom hooks.
- **Recharts** for the report charts.
- **React Router** for navigation.

Do not add a component library, a state-management library, or a data-fetching library
without being asked.

---

## Mockups

Reference designs live in `mockups/` (not committed to git). **Look at the relevant image
before building or changing a screen** — they are the source of truth for layout and styling.

| File | Screen |
|------|--------|
| `mockups/login.png` | Login — split layout, marketing panel left, form right |
| `mockups/register.png` | Register — same split layout |
| `mockups/chat.png` | Chat — messages, activity cards, composer |
| `mockups/chat-with-sidebar.png` | Chat with the conversation sidebar open |
| `mockups/chat-profile-menu.png` | Profile menu (Settings / Log out) |
| `mockups/settings-modal.png` | Settings modal — profile + tone |
| `mockups/timesheet-month-view.png` | Timesheet → Activities, Month calendar |
| `mockups/timesheet-week-view.png` | Timesheet → Activities, Week calendar |
| `mockups/timesheet-day-view.png` | Timesheet → Activities, Day calendar |
| `mockups/timesheet-activity-detail.png` | Activity detail drawer (right slide-over) |
| `mockups/timesheet-month-close.png` | Timesheet → Month Close tab |
| `mockups/reports-list.png` | Reports landing — list of available reports |
| `mockups/report-activity-comparison.png` | Activity Comparison — bar chart + Ask panel |
| `mockups/report-activity-trends.png` | Activity Trends — line chart |
| `mockups/logo.png` | The WardLog logo (teal medical cross with waveform) |

The mockups have some rough edges; follow their intent and layout, not every pixel. Where a
mockup and this file disagree on a colour, this file's tokens win.

---

## Design tokens

Dark theme throughout. These hex values were sampled from the mockups. Put them in the
Tailwind config as named tokens rather than scattering hex values through the markup.

### Surfaces
| Token | Hex | Use |
|-------|-----|-----|
| `bg` | `#15181a` | Page background, icon rail, empty calendar cells |
| `surface` | `#1b1f22` | Cards, panels, modals, chart containers |
| `surface-raised` | `#1d2124` | Activity cards in chat, list rows |
| `input` | `#22272a` | Form inputs, search fields |

### Accent (teal)
| Token | Hex | Use |
|-------|-----|-----|
| `accent` | `#17a398` | Primary buttons, logo tile, active tabs, links |
| `accent-strong` | `#3ecebd` | Bright teal — headline figures ("45h"), clinic block |
| `accent-muted` | `#173430` | User message bubbles, chip backgrounds on dark |

### Activity type colours
Used **consistently everywhere** — chart bars and lines, calendar event chips, progress bars,
and type chips. Never substitute other colours for these.

| Type | Hex |
|------|-----|
| Clinic Block | `#3ecebd` (teal) |
| Surgery Block | `#f4c876` (amber) |
| On-Call | `#7fa8e8` (blue) |
| Onsite On-Call | `#c9a6f0` (purple) |

On dark backgrounds these appear as the text/border colour with a low-opacity fill of the same
hue behind them (see the calendar event chips and the chat activity cards).

### Text
| Token | Use |
|-------|-----|
| `text` — near-white | Headings, primary content |
| `text-muted` — mid grey | Subtitles, secondary detail, placeholders |
| `text-subtle` — dim grey | Labels, timestamps, helper text |

### Shape & spacing
- Cards and panels: rounded ~12px, 1px subtle border slightly lighter than the surface
- Pills / chips / tabs: fully rounded
- Buttons: rounded ~8px
- Generous padding — the design breathes; do not crowd elements

---

## Layout

A **narrow icon rail** on the far left, persistent across all authenticated routes:
- WardLog logo tile at the top (teal, rounded) — use the actual logo icon from
  `mockups/logo.png`, **not** a letter "W" placeholder
- Chat, Timesheet, Reports icons
- User avatar at the bottom, opening the profile menu (Settings / Log out)

Chat additionally has a **collapsible conversation sidebar** ("New chat" + recents).
Auth screens have no rail — they use the split marketing/form layout.

---

## Routes

| Route | Screen |
|-------|--------|
| `/login` | Login |
| `/register` | Register |
| `/chat` | Chat (default after login) |
| `/chat/:conversationId` | A specific conversation |
| `/timesheet` | Timesheet — Activities / Month Close tabs |
| `/reports` | Reports list |
| `/reports/activity-comparison` | Activity Comparison |
| `/reports/activity-trends` | Activity Trends |

All routes except `/login` and `/register` require authentication.

---

## API access

**Everything goes through the API Gateway** — a single base URL from an env var
(`VITE_API_BASE_URL`). Never call a backend service directly.

Auth: the User service issues a short-lived access token and a refresh token on login. Send
the access token as `Authorization: Bearer <token>` on every request. On a 401, use the refresh
token to get a new access token and retry; if that fails, send the user to `/login`.

After a profile update, refresh the token — profile fields (name, tone, assistant name) are
carried as JWT claims, so the change only takes effect once a new access token is issued.

---

## Screen notes

### Chat
The assistant drafts activities and **nothing is logged until the doctor accepts** — the
footer says so, and activity cards carry accept/edit affordances with an "✓ Accepted" state.
The composer has: attach (+), a **Rush** toggle, a mic button, and send. Rush and voice output
are per-message flags sent with the request, not saved settings.

Some assistant replies pause for the doctor to choose between options (e.g. which activity a
patient belongs to) — the API returns an interrupt payload instead of a reply, and the choice
is sent back to a resume endpoint.

### Timesheet
Two tabs: **Activities** (Month / Week / Day calendar views; clicking an activity opens the
right-hand detail drawer) and **Month Close** (stat cards per activity type with progress
bars, then activities grouped by day, and a Close Month action).

Closing a month is permanent — the UI should make that clear before confirming.

### Reports
A list page leading to each report. Each report has its own filters (date range presets +
custom range, and a metric toggle between Number of Activities and Hours Worked). The API
returns both metrics at once, so **toggling the metric must not refetch** — switch
client-side.

Activity Trends also has a type filter (All / individual types) which is likewise
**client-side** — the API always returns all four types.

The **"Ask about this report"** panel sends the report's JSON to the AI service for a
narrative answer. That is a separate call the frontend makes after fetching the report data —
the reports API itself has no AI involvement.

---

## Structure

Feature-based, with shared pieces lifted out:

```
src/
  api/          # fetch wrappers, one module per backend area
  components/   # shared presentational components (Button, Input, Card, ...)
  features/
    auth/
    chat/
    timesheet/
    reports/
  hooks/
  lib/          # helpers (date formatting, activity-type colour lookup, ...)
  routes/
  types/        # shared TypeScript types mirroring API responses
```

Each feature folder holds its own components, hooks, and types. Anything used by two or more
features moves up to `components/`, `hooks/`, or `lib/`.
