export default {
  'action.registration.title': 'Реєстрація',
  'action.registration.description': 'Потрібно пройти 3 кроки',
  'action.start.title': 'Почати',
  'action.next.title': 'Далі',
  'action.finish.title': 'Завершити',
  'action.login.title': 'Вхід в акаунт',
  'action.enter.title': 'Увійти',
  'field.name.placeholder': "Твоє ім'я",
  'field.course.placeholder': 'Unity 3D',
  'field.group.placeholder': 'Група 2',
  'field.group.label': 'Група',
  'field.password.show': 'Показати пароль',
  'field.password.hide': 'Приховати пароль',
  'caption.has-account': 'Маєш акаунт?{#br/}{#a to=$to}Увійти{/a}',
  'caption.has-no-account': 'Немає акаунту?{#br/}{#a to=$to}Зареєструватися{/a}',
  'caption.mistake': 'Помилився?{#br/}{#a to=$to}Повернутся назад{/a}',
  'step.course-select.title': 'Твій курс',
  'step.avatar.title': 'Обери аватар',
  'step.view.title': 'Правильно?',
  'text.group': 'Група',
  'group.select.title': 'Обери групу',
  'group.filter.all': 'Всі ({$count :number})',
  'group.theme.game-dev': 'GameDev',
  'group.theme.web': 'Web',
  'group.theme.embedded': 'Embedded',
  'group.students-count': `
    .input {$count :number}
    .match $count
    one {{{$count} учень}}
    few {{{$count} учні}}
    many {{{$count} учнів}}
    * {{{$count} учня}}`,
  'group.back': 'Назад до вибору груп',
  'student.empty': 'Учнів за вашим запитом не знайдено',
  'field.student-search.placeholder': 'Пошук учня за іменем...',
  'action.clear-search.title': 'Очистити пошук',
  'sort.title': 'Сортування',
  'sort.students': 'Сортування учнів',
  'sort.name-asc': "Ім'я: А → Я",
  'sort.name-desc': "Ім'я: Я → А",
  'sort.balance-desc': 'Баланс: за спаданням',
  'sort.balance-asc': 'Баланс: за зростанням',
  'award.reason.label': 'Оберіть причину',
  'award.history.title': 'Історія нагород',
  'award.history.empty': 'Історія нагород порожня',
  'action.revert.title': 'Скасувати',
  'reason.activity': 'Активність на уроці',
  'reason.homework': 'Домашнє завдання',
  'reason.teamwork': 'Допомога команді',
  'reason.answer': 'Гарна відповідь',
  'reason.initiative': 'Ініціатива',
  'reason.discipline': 'Порушення дисципліни',
  'reason.mistake': 'Помилкове нарахування',
  'reason.late': 'Запізнення на урок',
  'reason.incomplete': 'Невиконання завдання',
  'reason.other': 'Інше',
  'profile.balance.amount': '{$count :number}',
  'profile.balance.caption': `
    .input {$count :number}
    .match $count
    one {{робокоїн}}
    few {{робокоїни}}
    many {{робокоїнів}}
    * {{робокоїна}}`,
}
