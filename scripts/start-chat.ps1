# scripts/start-chat.ps1
# ПРИНУДИТЕЛЬНЫЙ СТАРТ ЧАТА - ИИ ОБЯЗАН ПРОЧЕСТЬ И ПОДТВЕРДИТЬ

Write-Host ""
Write-Host "🔴 🔴 🔴 П Р И Н У Д И Т Е Л Ь Н Ы Й   С Т А Р Т   Ч А Т А 🔴 🔴 🔴" -ForegroundColor Red -BackgroundColor White
Write-Host "=" * 80 -ForegroundColor Red
Write-Host ""

# ============================================
# 1. ЗАПУСК АВТОМАТИЧЕСКОЙ ПРОВЕРКИ
# ============================================
Write-Host "1️⃣  ЗАПУСК АВТОМАТИЧЕСКОЙ ПРОВЕРКИ ПРОЕКТА..." -ForegroundColor Cyan
Write-Host "   Выполняю: .\scripts\smart-start.ps1" -ForegroundColor Gray
Write-Host ""

# Запускаем smart-start
& ".\scripts\smart-start.ps1"

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Red
Write-Host ""

# ============================================
# 2. ПРИНУДИТЕЛЬНОЕ ОТОБРАЖЕНИЕ ПРАВИЛ
# ============================================
Write-Host "2️⃣  🔴 ВНИМАНИЕ ИИ! ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:" -ForegroundColor Red -BackgroundColor Yellow
Write-Host "   (Прочти и подтверди что понял)" -ForegroundColor Yellow
Write-Host ""

$rules = @"

╔══════════════════════════════════════════════════════════════════════╗
║                     О Б Я З А Т Е Л Ь Н Ы Е   П Р А В И Л А           ║
║                 для ИИ в этом чате (НЕ ИГНОРИРОВАТЬ!)                ║
╚══════════════════════════════════════════════════════════════════════╝

🎯 1. СТИЛЬ РАБОТЫ С РАЗРАБОТЧИКОМ:
   • Разработчик НОВИЧОК - объяснять КАЖДЫЙ шаг
   • ОДНА команда = ОДНО действие (не несколько сразу)
   • Формат каждой команды:
     1. # КОМАНДА: [команда PowerShell]
     2. # ЧТО ДЕЛАЕТ: [объяснение]
     3. # РЕЗУЛЬТАТ: [что увидит разработчик]
     4. # ВАШИ ДЕЙСТВИЯ: [конкретные шаги]
     5. Ждать выполнения и отчёта

🎯 2. ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ:
   • Работать ТОЛЬКО когда видно (.venv) в начале строки PowerShell
   • Если нет (.venv) → сказать разработчику активировать .venv
   • Проверять импорты ПЕРЕД любым изменением кода
   • Не работать в ветке main/master
   • Следовать структуре проекта из docs/PROJECT_GUIDE.md

🎯 3. ПРАВИЛА БЕЗОПАСНОСТИ:
   • НИКАКИХ упоминаний WB/Ozon/Яндекс.Маркет
   • Использовать нейтральные термины: "площадка", "маркетплейс", "заказ"
   • Не предлагать нарушать правила маркетплейсов

🎯 4. ПРОЦЕСС РАЗРАБОТКИ:
   1. Проверить окружение (этот скрипт)
   2. Прочитать docs/PROJECT_GUIDE.md
   3. Давать по одной команде за раз
   4. Ждать выполнения
   5. Проверять результат
   6. Только потом следующая команда

🚫 НАРУШЕНИЕ ЭТИХ ПРАВИЛ = НЕПРАВИЛЬНАЯ РАБОТА
✅ СОБЛЮДЕНИЕ ПРАВИЛ = ПРОФЕССИОНАЛЬНАЯ РАБОТА

"@

Write-Host $rules -ForegroundColor Yellow
Write-Host ""

# ============================================
# 3. ПРИНУДИТЕЛЬНОЕ ТРЕБОВАНИЕ К ПРОЕКТУ
# ============================================
Write-Host "3️⃣  📚 ОБЯЗАТЕЛЬНЫЙ ФАЙЛ ДЛЯ ИИ:" -ForegroundColor Magenta
Write-Host "   docs/PROJECT_GUIDE.md - полный стандарт разработки" -ForegroundColor Gray

if (Test-Path "docs/PROJECT_GUIDE.md") {
    # Показываем первые 5 строк чтобы ИИ видел что файл существует
    $guidePreview = Get-Content "docs/PROJECT_GUIDE.md" -TotalCount 5 -Encoding UTF8
    Write-Host "   📋 Содержание (первые 5 строк):" -ForegroundColor Cyan
    foreach ($line in $guidePreview) {
        Write-Host "      $line" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "   ✅ Файл существует. ИИ ДОЛЖЕН его использовать!" -ForegroundColor Green
} else {
    Write-Host "   ❌ ФАЙЛ НЕ НАЙДЕН! КРИТИЧЕСКАЯ ОШИБКА!" -ForegroundColor Red
    Write-Host "      ИИ будет работать БЕЗ стандарта!" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# 4. ТРЕБОВАНИЕ ПОДТВЕРЖДЕНИЯ ОТ ИИ
# ============================================
Write-Host "4️⃣  ✅ ТРЕБУЕТСЯ ПОДТВЕРЖДЕНИЕ ОТ ИИ:" -ForegroundColor Green -BackgroundColor DarkBlue
Write-Host ""
Write-Host "   ИИ должен ответить:" -ForegroundColor White
Write-Host "   \"✅ ПОНЯЛ ПРАВИЛА. Буду работать по стандарту:\"" -ForegroundColor Green
Write-Host "   1. Следовать docs/PROJECT_GUIDE.md" -ForegroundColor Gray
Write-Host "   2. Давать команды с объяснением" -ForegroundColor Gray
Write-Host "   3. Ждать выполнения перед следующим шагом" -ForegroundColor Gray
Write-Host "   4. Работать только в (.venv) окружении" -ForegroundColor Gray
Write-Host ""
Write-Host "   🚀 ТОЛЬКО ПОСЛЕ этого подтверждения можно начинать работу!" -ForegroundColor Cyan
Write-Host ""

# ============================================
# 5. БЫСТРАЯ ПРОВЕРКА ОКРУЖЕНИЯ
# ============================================
Write-Host "5️⃣  ⚡ БЫСТРАЯ ПРОВЕРКА (для ИИ):" -ForegroundColor Blue
Write-Host ""

# Проверка .venv
if (Test-Path ".venv") {
    Write-Host "   • .venv: ✅ найден" -ForegroundColor Green
} else {
    Write-Host "   • .venv: ❌ НЕ НАЙДЕН!" -ForegroundColor Red
}

# Проверка кодировки
try {
    $encoding = [System.Console]::OutputEncoding.EncodingName
    Write-Host "   • Кодировка: $encoding" -ForegroundColor Green
} catch {
    Write-Host "   • Кодировка: ⚠️ не проверена" -ForegroundColor Yellow
}

# Проверка ветки git
try {
    $branch = git branch --show-current 2>$null
    if ($branch) {
        Write-Host "   • Git ветка: $branch" -ForegroundColor Green
        if ($branch -match "main|master") {
            Write-Host "     ⚠️  ВНИМАНИЕ: Работа в main ветке!" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "   • Git ветка: ⚠️ не проверена" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Red
Write-Host "🎯 СКРИПТ ЗАВЕРШЁН. ЖДУ ПОДТВЕРЖДЕНИЯ ОТ ИИ." -ForegroundColor Green
Write-Host "📋 Начинать работу МОЖНО только после подтверждения!" -ForegroundColor Cyan
Write-Host ""