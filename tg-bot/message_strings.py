class Messages:
    cmd_start = 'Привет! Я - вспомогательный бот для навыка Алисы "Моя лента".\n' \
                'Если Вы еще не воспользовались этим навыком, скажите Алисе "Запусти навык Моя лента".\n' \
                'После воспользуйтесь клавиатурой, чтобы связать Алису и Ваш телеграм.'

    code_entry = 'Введите код, который вам сказала Алиса'
    code_auth_first = 'Сперва мне нужно связать ваш телеграм аккаунт с Алисой. Скажите ей "Запусти навык Моя лента", и после она скажет Ваш шестизначный код.\n' \
                      'Его-то мне и пришлите :)'
    code_invalid = 'Упс, такого кода нет в базе! Код от Алисы - шестизначное число. Кажется, вы отправили мне что-то не то.'
    code_checking = 'Проверяю введенный вами код...'
    code_valid = 'Все отлично! Теперь скажите Алисе "Готово"'

    code_alice_checking = 'Проверяю, все ли хорошо...'
    code_alice_error = 'Упс! Алиса не подтвердила, что вы ей сказали "Готово". Попробуйте еще раз'
    code_alice_ok = 'Отлично! Ваш телеграм аккаунт связан с Алисой! Сейчас напишу Вам, что я умею'

    help = 'Небольшой FAQ обо мне:' \
           '\nСамое главное - пользуйтесь клавиатурой! Так я смогу точно понять, что вы от меня хотите.'

class UserReplies:
    enter_code = 'Ввести код'
    code_alice_approved = 'Сказал'