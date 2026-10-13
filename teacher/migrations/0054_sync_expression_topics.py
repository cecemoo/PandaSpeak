from django.db import migrations

# Existing expression topics previously lived only in the student view.
EXPRESSION_TOPICS = {
        'daily life': [
            'Greetings & Politeness', 'Everyday Activities',
            'Communication & Conversation', 'Habits & Routines',
            'Decisions & Choices', 'Requests & Responses', 'Common Situations',
            'Emotions & Reactions', 'Behavior & Personality', 'Difficulties & Challenges',
        ],
        'life & philosophy': [
            'Wisdom & Life Lessons', 'Values & Principles',
            'Happiness & Contentment', 'Personal Growth',
            'Attitude & Mindset', 'Success & Failure', 'Time & Opportunity',
            'Cause & Effect', 'Human Nature & Relationships',
        ],
        'weather': ["Pleasant Weather & Scenery","Wind & Storms","Rain & Thunder","Extreme Weather","Weather Metaphors & Life Lessons"],
        'society & resource': ["Resources & Value","Wealth & Social Status","Public Welfare & Responsibility","Cooperation & Interdependence","Social Behavior & Opportunity"],
        'emotions': ["Anger & Frustration","Fear & Anxiety","Joy & Excitement","Sadness & Grief","Surprise & Mixed Feelings"],
        'work & career': ["Hard Work & Dedication","Career Success & Achievement","Workplace Challenges & Setbacks"],
        'people': ["Personality & Character","Speech & Behavior","Judgment & Perception","Difficulties & Survival","Humor & Everyday Sayings"],
        'food and dining': ["Food & Ingredients","Cooking & Preparation","Eating & Appetite","Taste & Flavor","Dining Etiquette & Sharing"],
        'nature': ["Nature & Landscapes","Weather & Seasons","Plants & Flowers","Fire, Water & Natural Forces","Nature as Metaphor"],
        'problems & challenges & situations': ["Difficulties & Setbacks","Causes & Consequences","Solutions & Coping","Conflict & Dilemmas","Unexpected Situations"],
        'animals': ["Courage & Strength","Success & Achievement","Wisdom & Strategy","Personality & Behavior","Danger & Difficulties","Relationships & Society","Animal Characteristics & Comparisons"],
    'numbers': ["Unity & Consistency","Actions & Decisions","Numbers & Quantities","Perfection & Repetition","Emotions & Feelings"],
    'colors': ["Colors & Appearance","Clarity & Truth","Emotions & Facial Expressions","Success & Recognition","Descriptions & Metaphors"],
    'body parts': ["Eyes & Observation","Ears & Listening","Mouth & Speech","Heart & Emotions","Hands, Feet & Actions","Physical Appearance & Health","Mindset & Character","Human Relationships"],
    'family & relationships': ["Family Harmony & Values","Marriage & Couples","Parenting & Children","Family Duties & Support","Family Conflict & Difficulties","Love & Relationships","Relatives & Generations","Social Customs & Roles"],
            'time & dates': ["Time Is Precious","Punctuality & Timing","Time Management & Productivity","Passing Time & Change","Patience & Waiting","Opportunities & Deadlines","Seasons & Passage of Time"],
            'friendship': ["Making Friends","Trust & Loyalty","Support & Encouragement","Friendship & Affection","Conflict & Reconciliation","Social Relationships","Friendship & Betrayal"],
    }

def sync_existing_topics(apps, schema_editor):
    Category = apps.get_model('teacher', 'IdiomCategory')
    Idiom = apps.get_model('teacher', 'Idiom')
    Sub = apps.get_model('teacher', 'LearningSubcategory')
    for category in Category.objects.all():
        names = set(EXPRESSION_TOPICS.get(category.category_name.strip().lower(), []))
        names.update(Idiom.objects.filter(category_id=category.pk).exclude(subcategory='').values_list('subcategory', flat=True).distinct())
        for name in names:
            if name:
                Sub.objects.get_or_create(material_type='expression', category_id_value=category.pk, name=name)

class Migration(migrations.Migration):
    dependencies = [('teacher', '0053_learning_subcategories')]
    operations = [migrations.RunPython(sync_existing_topics, migrations.RunPython.noop)]
