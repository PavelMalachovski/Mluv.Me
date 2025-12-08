# 🐛 Исправление: Settings API Errors

## Проблема

При попытке изменить уровень чешского или другие настройки в WebUI возникала ошибка:
```
Error: Failed to update level. Please try again.
```

## Причина

Frontend отправлял запросы на несуществующие endpoints:
- ❌ `PATCH /api/v1/users/me` (не существует)
- ❌ `PATCH /api/v1/users/me/settings` (не существует)
- ❌ `GET /api/v1/stats/me` (не существует)

Backend использует endpoints с `user_id`:
- ✅ `PATCH /api/v1/users/{user_id}`
- ✅ `PATCH /api/v1/users/{user_id}/settings`
- ✅ `GET /api/v1/stats/summary?user_id={user_id}`

## Исправления

### 1. Settings Page
**Файл:** `frontend/app/dashboard/settings/page.tsx`

**Изменения:**
```typescript
// ДО:
queryFn: () => apiClient.get("/api/v1/users/me/settings")
mutationFn: (data) => apiClient.patch("/api/v1/users/me", data)

// ПОСЛЕ:
queryFn: () => apiClient.get(`/api/v1/users/${user?.id}/settings`)
mutationFn: (data) => apiClient.patch(`/api/v1/users/${user?.id}`, data)
```

**Добавлено:**
- Логирование ошибок в консоль для отладки
- Обновление user в auth store после изменения level
- Показ детального сообщения об ошибке из API
- Проверка `user?.id` перед запросом

### 2. Profile Page
**Файл:** `frontend/app/dashboard/profile/page.tsx`

**Изменения:**
```typescript
// ДО:
queryFn: () => apiClient.get("/api/v1/stats/me")

// ПОСЛЕ:
queryFn: () => apiClient.getStats(user!.id)
```

**Добавлено:**
- Использование существующего метода `apiClient.getStats()`
- Правильная передача `user_id`

### 3. Query Keys
Обновлены ключи React Query для корректной инвалидации:
```typescript
// ДО:
queryKey: ["user-settings"]
queryKey: ["user-stats"]

// ПОСЛЕ:
queryKey: ["user-settings", user?.id]
queryKey: ["user-stats", user?.id]
```

## Тестирование

### 1. Изменение уровня чешского
- [x] Открыть Settings → Learning
- [x] Нажать на любой уровень (Beginner/Intermediate/Advanced/Native)
- [x] Должен появиться спиннер загрузки
- [x] Должно появиться зеленое уведомление "Level updated"
- [x] Уровень должен сохраниться в профиле

### 2. Изменение настроек
- [x] Correction Level - должно сохраняться
- [x] Conversation Style - должно сохраняться
- [x] Voice Speed - должно сохраняться
- [x] Notifications - должно переключаться

### 3. Профиль
- [x] Статистика загружается корректно
- [x] Показывается актуальный уровень
- [x] Отображаются все metrics

## API Endpoints Используемые

### User Management
```
GET    /api/v1/users/{user_id}              - Получить пользователя
PATCH  /api/v1/users/{user_id}              - Обновить профиль (level)
GET    /api/v1/users/{user_id}/settings     - Получить настройки
PATCH  /api/v1/users/{user_id}/settings     - Обновить настройки
```

### Statistics
```
GET /api/v1/stats/summary?user_id={user_id}  - Получить статистику
GET /api/v1/stats/streak?user_id={user_id}   - Получить streak
```

## Дополнительные Улучшения

### Error Handling
Теперь показываются детальные ошибки:
```typescript
onError: (error: any) => {
  console.error("Settings update error:", error)
  toast({
    title: "Error",
    description: error?.response?.data?.detail || "Failed to update settings.",
    variant: "error",
  })
}
```

### State Management
После обновления level, данные обновляются в auth store:
```typescript
onSuccess: (updatedUser) => {
  useAuthStore.getState().updateUser({ level: updatedUser.level })
  // ...
}
```

## Результат

✅ **Все настройки теперь корректно сохраняются**
✅ **Уведомления работают правильно**
✅ **Ошибки показывают детальную информацию**
✅ **State синхронизируется корректно**

## Файлы Изменены

1. `frontend/app/dashboard/settings/page.tsx` - исправлены API calls
2. `frontend/app/dashboard/profile/page.tsx` - исправлен запрос статистики

## Build Status

```bash
cd frontend && npm run build
```
✅ **Сборка успешна - ошибок нет**

---

**Исправлено:** 8 декабря 2025
**Status:** ✅ RESOLVED
