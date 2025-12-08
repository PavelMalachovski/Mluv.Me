# 🧪 Local Build Testing Guide

## Before Pushing to GitHub/Railway

Always test the build locally to catch ESLint errors and TypeScript issues before deployment.

## Quick Test Commands

### 1. Full Production Build (Recommended)
```bash
cd frontend
npm run build
```

This runs:
- Next.js compilation
- TypeScript type checking
- ESLint validation
- Production optimization

**Expected output:**
```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Creating an optimized production build
```

### 2. Development Server (For Manual Testing)
```bash
cd frontend
npm run dev
```

Visit: `http://localhost:3000`

### 3. TypeScript Check Only
```bash
cd frontend
npx tsc --noEmit
```

### 4. ESLint Check Only
```bash
cd frontend
npx next lint
```

## Common ESLint Errors & Fixes

### Error: `react/no-unescaped-entities`

❌ **Wrong:**
```tsx
<p>Don't use quotes "like this"</p>
<p>Honzík's personality</p>
```

✅ **Correct:**
```tsx
<p>Don&apos;t use quotes &ldquo;like this&rdquo;</p>
<p>Honzík&apos;s personality</p>
```

### Common Escape Codes
- `'` → `&apos;` or `&#39;`
- `"` → `&quot;` or `&ldquo;` / `&rdquo;`
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`

## Automated Build Testing Script

### Windows PowerShell
```powershell
# Save as test-build.ps1
cd C:\Git\Mluv.Me\frontend
Write-Host "🧪 Testing production build..." -ForegroundColor Cyan

npm run build
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful!" -ForegroundColor Green
} else {
    Write-Host "❌ Build failed! Fix errors before pushing." -ForegroundColor Red
    exit 1
}
```

Run: `.\test-build.ps1`

### Unix/Mac/Linux
```bash
# Save as test-build.sh
#!/bin/bash
cd frontend
echo "🧪 Testing production build..."

npm run build
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
else
    echo "❌ Build failed! Fix errors before pushing."
    exit 1
fi
```

Run: `chmod +x test-build.sh && ./test-build.sh`

## Pre-Commit Checklist

Before pushing code:

- [ ] Run `npm run build` successfully
- [ ] Check console for any warnings
- [ ] Test key pages manually (if UI changes)
- [ ] Run `git status` to review changes
- [ ] Write clear commit message

## CI/CD Pipeline

Railway automatically runs:
1. `npm ci` or `npm install`
2. `npm run build`
3. Deployment (if build succeeds)

**Build failures stop deployment** - that's why local testing is crucial!

## Debugging Build Failures

### 1. Clear Cache
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### 2. Check Node Version
```bash
node --version  # Should be 18.x or higher
npm --version
```

### 3. Review Error Messages
- ESLint errors show line numbers
- TypeScript errors show file and type issues
- Next.js errors show compilation problems

### 4. Common Issues
- Missing dependencies: `npm install`
- Outdated packages: `npm outdated`
- Type errors: Check imports and interfaces
- ESLint: Use proper escape codes

## Quick Fix for Most Issues
```bash
cd frontend
rm -rf .next
npm run build
```

## Testing Specific Pages

```bash
# Build and check specific routes
npm run build

# Then manually test:
# - /dashboard (Chat)
# - /dashboard/profile
# - /dashboard/saved
# - /dashboard/settings
```

## Performance Testing

```bash
cd frontend
npm run build

# Check bundle size
ls -lh .next/static/chunks/

# Analyze bundle
npm install -g @next/bundle-analyzer
ANALYZE=true npm run build
```

## Summary

✅ **Always run `npm run build` before pushing**
✅ **Fix all ESLint and TypeScript errors**
✅ **Test locally in dev mode: `npm run dev`**
✅ **Review Railway logs after deployment**

---

**Happy coding! 🚀**
