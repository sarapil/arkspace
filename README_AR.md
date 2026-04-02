<p align="center">
  <img src="arkspace/public/images/arkspace-logo-animated.svg" alt="شعار أرك سبيس" width="128">
</p>

<div dir="rtl">

# أرك سبيس — ARKSpace v6.0

> نظام إدارة مساحات العمل المشتركة للمؤسسات  
> متوافق مع Frappe v16 و ERPNext v16  
> **آخر تحديث:** 2026-03-21

## نظرة عامة

أرك سبيس هو منصة شاملة ثنائية اللغة (عربي/إنجليزي) لإدارة مساحات العمل المشتركة مبنية على إطار عمل Frappe. يتعامل مع الدورة الكاملة لعمليات مساحات العمل المشتركة: المساحات، الحجوزات، العضويات، إدارة علاقات العملاء، العقود، التدريب، والفوترة.

## البدء السريع

```bash
cd frappe-bench
bench get-app arkspace
bench --site dev.localhost install-app arkspace
bench --site dev.localhost migrate
bench build --app arkspace
bench start
```

## الوحدات (9)

| الوحدة | الوصف |
|--------|-------|
| الإعدادات الأساسية | الإعدادات والأدوات المساعدة |
| المساحات | أنواع المساحات والوحدات والحجوزات |
| العضويات | الخطط والاشتراكات ومحافظ الرصيد |
| إدارة العملاء | العملاء المحتملون والجولات وخط المبيعات |
| العقود | القوالب والمستندات القانونية وإيصالات الدفع |
| التدريب | الوحدات والجلسات والشارات والتقدم |
| التكاملات | جسر فوترة ERPNext |
| التوثيق | التوثيق التلقائي |
| التصميم | الألوان والأيقونات والتخصيص و RTL |

## الإحصائيات

| المقياس | العدد |
|---------|-------|
| أنواع المستندات | 25 (18 مستقلة + 7 جداول فرعية) |
| نقاط API | ~30 |
| أدوار مخصصة | 7 |
| سير عمل | 3 |
| مهام مجدولة | 7 |
| تنسيقات طباعة | 7 |
| إشعارات | 4 |
| تقارير | 3 |

## التوثيق

| الملف | الغرض |
|-------|-------|
| [docs/FEATURES_AR.md](docs/FEATURES_AR.md) | مميزات التطبيق بالعربية |
| [docs/FEATURES_EN.md](docs/FEATURES_EN.md) | الميزات الكاملة بالإنجليزية |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | مرجع واجهة البرمجة |
| [docs/DOCTYPES_REFERENCE.md](docs/DOCTYPES_REFERENCE.md) | مخططات أنواع المستندات |
| [docs/TECHNICAL_IMPLEMENTATION.md](docs/TECHNICAL_IMPLEMENTATION.md) | التنفيذ التقني |
| [docs/ADMIN_GUIDE.md](docs/ADMIN_GUIDE.md) | دليل المسؤول |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | دليل المستخدم |
| [docs/ROADMAP.md](docs/ROADMAP.md) | خارطة الطريق |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | استكشاف الأخطاء |
| [CHANGELOG.md](CHANGELOG.md) | سجل التغييرات |
| [CONTRIBUTING.md](CONTRIBUTING.md) | دليل المساهمة |

## الترخيص

MIT

</div>
