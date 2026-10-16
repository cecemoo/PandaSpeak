from django.db import migrations

# Titles are copied from the existing student learning page groupings.
# Keep the original bilingual labels rather than introducing new categories.
VOCABULARY = {
  "food": [
    "Fruits 水果",
    "Vegetables 蔬菜",
    "Meat & Seafood 肉類與海鮮",
    "Drinks 飲料",
    "Meals & Dishes 餐點與料理"
  ],
  "food and dining": [
    "Fruits 水果",
    "Vegetables 蔬菜",
    "Meat & Seafood 肉類與海鮮",
    "Drinks 飲料",
    "Meals & Dishes 餐點與料理"
  ],
  "animals": [
    "Pets 寵物",
    "Farm Animals 農場動物",
    "Wild Animals 野生動物",
    "Birds 鳥類",
    "Aquatic Animals 水生動物"
  ],
  "colors": [
    "Basic Colors 基本顏色",
    "Light & Dark Colors 深淺顏色",
    "Color Descriptions 顏色描述"
  ],
  "colours": [
    "Basic Colors 基本顏色",
    "Light & Dark Colors 深淺顏色",
    "Color Descriptions 顏色描述"
  ],
  "body parts": [
    "Head & Face 頭部與臉部",
    "Upper Body 上半身",
    "Lower Body 下半身",
    "Internal Organs 內臟器官"
  ],
  "greetings": [
    "Basic Greetings 基本問候",
    "Introductions 自我介紹",
    "Farewells 道別",
    "Polite Expressions 禮貌用語"
  ],
  "time and dates": [
    "Time of Day 一天中的時間",
    "Days & Weeks 日期與星期",
    "Months & Years 月份與年份",
    "Time Expressions 時間表達"
  ],
  "time & dates": [
    "Time of Day 一天中的時間",
    "Days & Weeks 日期與星期",
    "Months & Years 月份與年份",
    "Time Expressions 時間表達"
  ],
  "shopping": [
    "Stores & Shopping Places 商店與購物場所",
    "Prices & Payment 價格與付款",
    "Clothing & Sizes 衣服與尺寸",
    "Shopping Actions 購物動作"
  ],
  "daily life": [
    "Morning & Evening Routines 早晚作息",
    "Household Activities 家務活動",
    "Daily Activities 日常活動",
    "Home & Personal Items 居家與個人物品"
  ],
  "emotions": [
    "Happiness & Positive Feelings 快樂與正面情緒",
    "Sadness & Negative Feelings 悲傷與負面情緒",
    "Anger & Frustration 生氣與挫折",
    "Fear & Worry 害怕與擔心",
    "Surprise & Mixed Feelings 驚訝與複雜感受"
  ],
  "pronouns": [
    "Personal Pronouns 人稱代名詞",
    "Possessive Pronouns 所有格代名詞",
    "Demonstrative Pronouns 指示代名詞",
    "Interrogative Pronouns 疑問代名詞",
    "Reflexive & Indefinite Pronouns 反身與不定代名詞"
  ],
  "possessives": [
    "Singular Possessives 單數所有格",
    "Plural Possessives 複數所有格",
    "Family & Relationships 家庭與人際關係",
    "Ownership & Possession 所有權與歸屬"
  ],
  "places & location": [
    "Places in the City 城市場所",
    "Home & Buildings 家庭與建築",
    "Directions & Positions 方向與位置",
    "Travel & Transportation 交通與出行",
    "Distance & Location Descriptions 距離與地點描述"
  ],
  "demonstratives": [
    "This & That 這與那",
    "These & Those 這些與那些",
    "Here & There 這裡與那裡",
    "This Way & That Way 這樣與那樣",
    "Which & Comparison 哪個與比較"
  ],
  "adjectives": [
    "Size & Shape 大小與形狀",
    "Appearance & Qualities 外觀與特質",
    "Personality & Character 個性與性格",
    "Feelings & Conditions 感受與狀態",
    "Taste & Sensory Descriptions 味道與感官",
    "Value & Difficulty 價值與難易",
    "Speed, Amount & Degree 速度數量與程度"
  ],
  "verbs": [
    "Everyday Actions 日常動作",
    "Movement & Travel 移動與交通",
    "Eating & Drinking 飲食動作",
    "Speaking & Communication 說話與溝通",
    "Thinking & Learning 思考與學習",
    "Seeing, Hearing & Sensing 感官與觀察",
    "Work, Shopping & Transactions 工作與購物",
    "Feelings & Relationships 情感與人際互動",
    "Change & Results 變化與結果"
  ],
  "learning & communication": [
    "Learning & Studying 學習與讀書",
    "Understanding & Thinking 理解與思考",
    "Speaking & Conversation 說話與對話",
    "Listening & Pronunciation 聽力與發音",
    "Reading & Writing 閱讀與寫作",
    "Messages & Digital Communication 訊息與數位溝通",
    "Classroom & Feedback 課堂與回饋"
  ],
  "numbers": [
    "Basic Numbers 基本數字",
    "Large Numbers & Place Values 大數字與位值",
    "Counting & Quantities 數量與計數",
    "Ordinal Numbers & Order 序數與順序",
    "Fractions, Decimals & Percentages 分數小數與百分比",
    "Math & Calculations 數學與計算",
    "Numbers in Daily Life 生活中的數字"
  ],
  "adverb": [
    "Time & Frequency 時間與頻率副詞",
    "Degree & Intensity 程度副詞",
    "Manner & Attitude 方式與態度副詞",
    "Place & Direction 地點與方向副詞",
    "Negation & Restriction 否定與限制副詞",
    "Possibility & Certainty 可能性與肯定副詞",
    "Connection & Emphasis 連接與強調副詞"
  ],
  "adverbs": [
    "Time & Frequency 時間與頻率副詞",
    "Degree & Intensity 程度副詞",
    "Manner & Attitude 方式與態度副詞",
    "Place & Direction 地點與方向副詞",
    "Negation & Restriction 否定與限制副詞",
    "Possibility & Certainty 可能性與肯定副詞",
    "Connection & Emphasis 連接與強調副詞"
  ],
  "abstract ideas / concepts": [
    "Ideas & Thinking 思想與思考",
    "Values & Morality 價值與道德",
    "Time & Change 時間與變化",
    "Emotions & Inner Life 情緒與內心世界",
    "Relationships & Society 關係與社會",
    "Possibility & Decisions 可能性與選擇",
    "Truth & Knowledge 真實與知識"
  ],
  "people": [
    "People & Identity 人物與身分",
    "Friends & Relationships 朋友與人際關係",
    "Occupations & Roles 職業與角色",
    "Community & Public Figures 社區與公眾人物",
    "Personality & Descriptions 個性與人物描述"
  ],
  "work & career": [
    "Workplace & People 職場與人員",
    "Daily Work & Tasks 日常工作與任務",
    "Job Search & Hiring 求職與招聘",
    "Pay & Benefits 薪資與福利",
    "Career Growth & Skills 職涯發展與技能",
    "Business & Management 商業與管理"
  ],
  "relationships & social interaction": [
    "Friendship & Companionship 友誼與陪伴",
    "Social Greetings & Courtesy 社交問候與禮貌",
    "Conversation & Socializing 交談與社交",
    "Feelings & Interpersonal Care 情感與人際關懷",
    "Conflict & Reconciliation 衝突與和解",
    "Relationships & Boundaries 關係與界線",
    "Community & Group Interaction 社群與團體互動"
  ],
  "entertainment & events": [
    "Movies & Television 電影與電視",
    "Music & Performances 音樂與表演",
    "Games & Hobbies 遊戲與休閒嗜好",
    "Sports & Outdoor Activities 運動與戶外活動",
    "Parties & Social Events 派對與社交活動",
    "Festivals & Celebrations 節日與慶典",
    "Travel & Cultural Events 旅遊與文化活動"
  ],
  "society & culture": [
    "Society & Community 社會與社區",
    "Culture & Traditions 文化與傳統",
    "Festivals & Customs 節慶與民俗",
    "Government & Civic Life 政府與公民生活",
    "Language & Cultural Expression 語言與文化表達",
    "Education & Social Institutions 教育與社會制度",
    "Environment & Social Issues 環境與社會議題"
  ],
  "family": [
    "Immediate Family 直系家庭成員",
    "Extended Family 大家庭成員",
    "Family Relationships 家庭關係"
  ],
  "weather": [
    "Weather Conditions 天氣狀況",
    "Temperature & Feelings 氣溫與感受",
    "Seasons 季節"
  ]
}
SENTENCE = {
  "greetings": [
    "Everyday Greetings 日常問候",
    "Morning & Evening Greetings 早晚問候",
    "Polite Expressions 禮貌用語",
    "Introductions 初次見面與介紹",
    "Farewells & Well Wishes 道別與祝福"
  ],
  "family": [
    "Introducing Family Members 介紹家庭成員",
    "Family Relationships 家庭關係",
    "Extended Family 大家庭與親戚",
    "Family Activities & Daily Life 家庭活動與日常生活",
    "Love, Care & Family Feelings 家庭情感與關懷",
    "Marriage & Family Milestones 婚姻與家庭重要時刻"
  ],
  "time and dates": [
    "Telling the Time 幾點與時間表達",
    "Days of the Week 星期與週末",
    "Calendar Dates 日期與月份",
    "Daily Schedule & Appointments 日常作息與約定",
    "Past, Present & Future 過去現在與未來",
    "Duration & Frequency 時間長短與頻率",
    "Seasons & Special Dates 季節與特別日子"
  ],
  "time & dates": [
    "Telling the Time 幾點與時間表達",
    "Days of the Week 星期與週末",
    "Calendar Dates 日期與月份",
    "Daily Schedule & Appointments 日常作息與約定",
    "Past, Present & Future 過去現在與未來",
    "Duration & Frequency 時間長短與頻率",
    "Seasons & Special Dates 季節與特別日子"
  ],
  "weather": [
    "Asking About the Weather 詢問天氣",
    "Sunny, Cloudy & Rainy Days 晴天陰天與雨天",
    "Temperature & Comfort 氣溫與冷熱感受",
    "Wind, Snow & Severe Weather 風雪與惡劣天氣",
    "Seasons & Seasonal Weather 四季與季節天氣",
    "Weather Forecasts & Plans 天氣預報與活動安排"
  ],
  "food and dining": [
    "Meals & Eating Habits 三餐與飲食習慣",
    "Food Preferences & Tastes 食物喜好與口味",
    "Ordering at a Restaurant 餐廳點餐",
    "Cooking & Preparing Food 烹飪與備餐",
    "Drinks & Beverages 飲料與喝水",
    "Paying & Restaurant Service 結帳與餐廳服務",
    "Dining Together & Invitations 邀約與一起用餐"
  ],
  "shopping": [
    "Asking Prices & Discounts 詢問價格與折扣",
    "Finding Stores & Products 找商店與商品",
    "Sizes, Colors & Trying Things On 尺寸顏色與試穿",
    "Choosing & Comparing Products 選擇與比較商品",
    "Checkout & Payment 結帳與付款",
    "Returns, Exchanges & Customer Service 退換貨與售後服務",
    "Online Shopping & Delivery 網購與配送"
  ],
  "making new friends": [
    "Meeting & Greeting New People 認識新朋友與打招呼",
    "Introducing Yourself 自我介紹",
    "Getting to Know Each Other 互相了解",
    "Starting & Keeping Conversations 開啟與延續話題",
    "Invitations & Making Plans 邀請與相約",
    "Exchanging Contact Information 交換聯絡方式",
    "Friendship & Staying in Touch 友誼與保持聯繫"
  ],
  "expressing feelings": [
    "Happiness & Excitement 快樂與興奮",
    "Sadness & Disappointment 難過與失望",
    "Anger & Frustration 生氣與挫折",
    "Fear, Worry & Nervousness 害怕擔心與緊張",
    "Love, Gratitude & Care 愛與感謝和關懷",
    "Surprise, Confusion & Curiosity 驚訝疑惑與好奇",
    "Expressing Opinions & Personal Feelings 表達想法與個人感受",
    "Comforting & Encouraging Others 安慰與鼓勵他人"
  ],
  "daily conversation": [
    "Everyday Greetings & Small Talk 日常問候與閒聊",
    "Daily Routines & Activities 日常作息與活動",
    "Asking Questions & Clarifying 詢問與確認",
    "Requests, Help & Permission 請求幫忙與徵求同意",
    "Making Plans & Appointments 安排行程與約定",
    "Opinions, Likes & Preferences 想法喜好與選擇",
    "Polite Responses & Social Expressions 禮貌回應與社交用語",
    "Problems & Everyday Situations 生活問題與應對"
  ],
  "health": [
    "Describing Symptoms 描述身體症狀",
    "Seeing a Doctor & Making Appointments 看醫生與預約",
    "Medicine & Treatment 藥物與治療",
    "Healthy Habits & Prevention 健康習慣與預防保健",
    "Body Parts & Physical Conditions 身體部位與身體狀況",
    "Mental Health & Emotional Well-being 心理健康與情緒照顧",
    "Emergencies & Getting Help 緊急狀況與求助"
  ]
}
# Names introduced by 0056 that were not part of the student page taxonomy.
GENERIC_VOCABULARY = {
  "people": [
    "Introducing People",
    "Describing People",
    "Relationships"
  ],
  "family": [
    "Introducing Family",
    "Family Activities",
    "Family Relationships"
  ],
  "daily life": [
    "Greetings",
    "Daily Routines",
    "Requests & Responses",
    "Everyday Conversations"
  ],
  "food": [
    "Ordering Food",
    "Food Preferences",
    "Cooking & Dining"
  ],
  "food and dining": [
    "Ordering Food",
    "Food Preferences",
    "Cooking & Dining"
  ],
  "animals": [
    "Describing Animals",
    "Animal Activities"
  ],
  "nature": [
    "Describing Nature",
    "Weather & Seasons",
    "Outdoor Activities"
  ],
  "numbers": [
    "Counting & Quantities",
    "Age",
    "Prices"
  ],
  "time & dates": [
    "Asking the Time",
    "Dates & Appointments",
    "Schedules"
  ],
  "weather": [
    "Describing Weather",
    "Weather Questions",
    "Seasons"
  ],
  "emotions": [
    "Expressing Feelings",
    "Asking About Feelings",
    "Reactions"
  ],
  "body parts": [
    "Describing the Body",
    "Health & Symptoms"
  ],
  "colors": [
    "Describing Colors",
    "Color Preferences"
  ],
  "shopping": [
    "Asking Prices",
    "Making Purchases",
    "Sizes & Quantities"
  ],
  "transportation": [
    "Asking Directions",
    "Travel Plans",
    "Public Transportation"
  ],
  "places": [
    "Home",
    "School",
    "Workplaces",
    "Public Places"
  ],
  "verbs": [
    "Actions",
    "Movement",
    "Communication",
    "Daily Activities"
  ],
  "adjectives": [
    "Appearance",
    "Size & Shape",
    "Quality",
    "Feelings"
  ],
  "adverbs": [
    "Time",
    "Frequency",
    "Manner",
    "Degree"
  ]
}
GENERIC_SENTENCE = {
  "friendship": [
    "Making Friends",
    "Conversations with Friends",
    "Friendship & Support"
  ]
}

def synchronize(apps, schema_editor):
    Sub = apps.get_model('teacher', 'LearningSubcategory')
    Vocabulary = apps.get_model('teacher', 'Vocabulary')
    Sentence = apps.get_model('teacher', 'Sentence')
    for kind, category_model, item_model, definitions, generic in (
        ('vocabulary', apps.get_model('teacher', 'VocabularyCategory'), Vocabulary, VOCABULARY, GENERIC_VOCABULARY),
        ('sentence', apps.get_model('teacher', 'SentenceCategory'), Sentence, SENTENCE, GENERIC_SENTENCE),
    ):
        for category in category_model.objects.all():
            key = category.category_name.strip().lower()
            canonical = definitions.get(key)
            if not canonical:
                continue
            for name in canonical:
                Sub.objects.get_or_create(material_type=kind, category_id_value=category.pk, name=name)
            # Delete only the accidental 0056 starter labels, never user-created
            # or in-use subcategories, and never a canonical label.
            for name in generic.get(key, []):
                if name in canonical:
                    continue
                if item_model.objects.filter(category_id=category.pk, subcategory=name).exists():
                    continue
                Sub.objects.filter(material_type=kind, category_id_value=category.pk, name=name).delete()

class Migration(migrations.Migration):
    dependencies = [('teacher', '0056_seed_vocabulary_sentence_subcategories')]
    operations = [migrations.RunPython(synchronize, migrations.RunPython.noop)]
