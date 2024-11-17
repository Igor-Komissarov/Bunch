import pandas as pd
import yaml

company = ''
# Загрузка файлов
restore_df = pd.read_excel('/Users/igorkomissarov/ProjectOffice_FIPS Dropbox/Игорь Комиссаров/WorkPlace/bunch/' + company + '/Restore_' + company +'.xlsx')
oak_tasks_df = pd.read_excel('/Users/igorkomissarov/ProjectOffice_FIPS Dropbox/Игорь Комиссаров/WorkPlace/bunch/' + company + '/' + company + '_patents_tasks.xlsx', skiprows=1, names=['Application Area', 'FAN IDs'])
ai_groups_df = pd.read_excel('/Users/igorkomissarov/ProjectOffice_FIPS Dropbox/Игорь Комиссаров/WorkPlace/bunch/' + company + '/' + company + '_patents_ai.xlsx', skiprows=1, names=['AI Technology/Application Area', 'FAN IDs'])

# Загрузка данных YAML
with open('/Users/igorkomissarov/ProjectOffice_FIPS Dropbox/Игорь Комиссаров/WorkPlace/website_rup/Configurations/etalon_yaml.yaml', 'r', encoding='utf-8') as file:
    yaml_data = yaml.safe_load(file)

# Извлечение тегов из YAML с очисткой пробелов
oak_task_groups = set(tag.strip() for tag in yaml_data.get('OAK_tasks', {}).get('ru', []))
oak_ai_groups = set(tag.strip() for tag in yaml_data.get('OAK_AI_groups', {}).get('ru', []))

# Файл для логов
#log_file_path = 'C:/website_orbit/website_rup/Logs/log_new.txt'

def format_tag(tag):
    # Преобразуем только первую букву в заглавную, оставляя остальные символы как есть
    return tag[0].upper() + tag[1:] if tag else tag

def add_tag_columns_and_populate(restore_df, oak_df, ai_df, oak_task_groups, oak_ai_groups):
    log_messages = []  # Список для хранения сообщений лога

    # Проверка на пустые значения в ключевых полях
    if restore_df['Questel unique family ID (FAN)'].isnull().any():
        log_messages.append("Внимание: Найдены пустые значения в колонке 'Questel unique family ID (FAN)' в Restore.")

    if oak_df['FAN IDs'].isnull().any():
        log_messages.append("Внимание: Найдены пустые значения в колонке 'FAN IDs' в файле OAK Tasks.")

    if ai_df['FAN IDs'].isnull().any():
        log_messages.append("Внимание: Найдены пустые значения в колонке 'FAN IDs' в файле AI Groups.")

    # Получаем уникальные теги из файлов OAK и AI, сверяя их с YAML
    oak_tags = [tag.strip() for tag in oak_df['Application Area'].dropna().unique() if tag.strip() in oak_task_groups]
    ai_tags = [tag.strip() for tag in ai_df['AI Technology/Application Area'].dropna().unique() if tag.strip() in oak_ai_groups]

    # Применяем форматирование тегов, только первую букву делаем заглавной
    oak_tags = [format_tag(tag) for tag in oak_tags]
    ai_tags = [format_tag(tag) for tag in ai_tags]

    # Объединяем все уникальные теги
    all_tags = list(set(oak_tags + ai_tags))
    
    # Убедимся, что количество тегов составляет 22
    if len(all_tags) < 22:
        missing_tags = list(oak_task_groups.union(oak_ai_groups) - set(all_tags))
        all_tags.extend([format_tag(tag) for tag in missing_tags])  # Добавляем недостающие теги с форматированием
        log_messages.append(f"Добавлены недостающие теги: {', '.join(missing_tags)}")

    # Приведение FAN к строковому формату
    restore_df['Questel unique family ID (FAN)'] = restore_df['Questel unique family ID (FAN)'].astype(str)

    # Добавляем колонки для каждого тега в restore_df
    for tag in all_tags:
        restore_df[tag] = 0  # По умолчанию ставим 0

    # Обновляем значения для каждого FAN
    for index, row in restore_df.iterrows():
        fan = row['Questel unique family ID (FAN)']

        # Проверка, найден ли FAN
        if not fan or fan == 'nan':
            log_messages.append(f"Пропущен FAN на строке {index + 2} из-за отсутствия значения.")
            continue

        # Проверяем наличие FAN в файле OAK
        oak_rows = oak_df[oak_df['FAN IDs'].astype(str).str.contains(fan)]
        if oak_rows.empty:
            log_messages.append(f"FAN {fan} не найден в файле OAK Tasks.")

        for _, oak_row in oak_rows.iterrows():
            tag = oak_row['Application Area'].strip()
            formatted_tag = format_tag(tag)
            # print(formatted_tag)
            # if formatted_tag == 'Навигационные задачи':
            #     print('ww')
            if formatted_tag in restore_df.columns:
                restore_df.at[index, formatted_tag] = 1  # Ставим 1 в соответствующей колонке тега

        # Проверяем наличие FAN в файле AI
        ai_rows = ai_df[ai_df['FAN IDs'].astype(str).str.contains(fan)]
        if ai_rows.empty:
            log_messages.append(f"FAN {fan} не найден в файле AI Groups.")

        for _, ai_row in ai_rows.iterrows():
            tag = ai_row['AI Technology/Application Area'].strip()
            formatted_tag = format_tag(tag)
            if formatted_tag in restore_df.columns:
                restore_df.at[index, formatted_tag] = 1  # Ставим 1 в соответствующей колонке тега

    # Запись логов в файл
    # with open(log_file_path, 'w', encoding='utf-8') as log_file:
    #     for message in log_messages:
    #         log_file.write(message + '\n')

    return restore_df

# Выполняем функцию и сохраняем результат
updated_restore_df = add_tag_columns_and_populate(restore_df, oak_tasks_df, ai_groups_df, oak_task_groups, oak_ai_groups)
output_path = '/Users/igorkomissarov/ProjectOffice_FIPS Dropbox/Игорь Комиссаров/WorkPlace/bunch/' + company + '/' + company + '.Реестр патентных документов.xlsx'
updated_restore_df.to_excel(output_path, index=False)
print(f"Файл сохранен по адресу: {output_path}")
#print(f"Лог сохранен по адресу: {log_file_path}")
