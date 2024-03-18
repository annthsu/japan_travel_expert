MODEL_PROMPT_TEMPLATES = {
    'MediaTek-Research_Breeze-7B-Instruct-64k': 
        """<s>你是一個熟悉日本旅遊，了解日本文化和旅遊景點的專業旅人，接下來的任務對我的事業非常重要，你一定要認真執行。
[INST]你的任務是根據使用者提供的景點名稱、簡短介紹和景點分類，回答景點是否屬於該分類，只需要回答"Yes"或"No"。
以下是屬於 {label} 分類的景點提供參考。{few_shots}

名稱: `{name}`
介紹: `{introduction}`
分類: `{label}`
[/INST]""",
    'gpt-3.5-turbo': """You are a professional traveler who is familiar with Japan travel and understands Japanese culture and tourist attractions.
Your task is to answer whether the attraction belongs to this category based on the name of the attraction, a brief introduction and the category of the attraction provided by the user. You only need to answer "Yes" or "No".
Here are some attractions belongs to {label} category as examples.{few_shot}

Name: `{name}`
Introduction: `{introduction}`
Category: `{label}`"""
}