from django.db import migrations

# Starter subcategories for existing learning categories. Existing manager-defined
# records are preserved; repeated runs cannot create duplicate records.
VOCABULARY = {
    'people': ['Family Members', 'Occupations & Roles', 'Personality & Character', 'Relationships', 'Descriptions of People'],
    'family': ['Immediate Family', 'Extended Family', 'Family Relationships'],
    'daily life': ['Daily Activities', 'Household Items', 'Personal Care', 'Routines'],
    'food': ['Food & Ingredients', 'Drinks', 'Cooking', 'Dining'],
    'food and dining': ['Food & Ingredients', 'Drinks', 'Cooking', 'Dining'],
    'animals': ['Pets', 'Wild Animals', 'Farm Animals', 'Birds', 'Sea Animals'],
    'nature': ['Plants & Flowers', 'Landscapes', 'Weather & Seasons', 'Natural Elements'],
    'numbers': ['Counting', 'Quantities', 'Large Numbers', 'Ordinal Numbers'],
    'time & dates': ['Time', 'Days & Weeks', 'Months & Years', 'Dates'],
    'weather': ['Weather Conditions', 'Temperature', 'Seasons'],
    'emotions': ['Positive Emotions', 'Negative Emotions', 'Feelings & Reactions'],
    'body parts': ['Head & Face', 'Upper Body', 'Lower Body', 'Internal Organs'],
    'colors': ['Basic Colors', 'Shades & Descriptions'],
    'shopping': ['Shopping Items', 'Prices & Payment', 'Sizes & Quantities'],
    'transportation': ['Vehicles', 'Travel & Directions', 'Public Transportation'],
    'places': ['Home', 'School', 'Workplaces', 'Public Places'],
    'verbs': ['Actions', 'Movement', 'Communication', 'Daily Activities'],
    'adjectives': ['Appearance', 'Size & Shape', 'Quality', 'Feelings'],
    'adverbs': ['Time', 'Frequency', 'Manner', 'Degree'],
}
SENTENCE = {
    'people': ['Introducing People', 'Describing People', 'Relationships'],
    'daily life': ['Greetings', 'Daily Routines', 'Requests & Responses', 'Everyday Conversations'],
    'family': ['Introducing Family', 'Family Activities', 'Family Relationships'],
    'food': ['Ordering Food', 'Food Preferences', 'Cooking & Dining'],
    'food and dining': ['Ordering Food', 'Food Preferences', 'Cooking & Dining'],
    'shopping': ['Asking Prices', 'Making Purchases', 'Sizes & Quantities'],
    'time & dates': ['Asking the Time', 'Dates & Appointments', 'Schedules'],
    'weather': ['Describing Weather', 'Weather Questions', 'Seasons'],
    'emotions': ['Expressing Feelings', 'Asking About Feelings', 'Reactions'],
    'transportation': ['Asking Directions', 'Travel Plans', 'Public Transportation'],
    'nature': ['Describing Nature', 'Weather & Seasons', 'Outdoor Activities'],
    'animals': ['Describing Animals', 'Animal Activities'],
    'numbers': ['Counting & Quantities', 'Age', 'Prices'],
    'colors': ['Describing Colors', 'Color Preferences'],
    'body parts': ['Describing the Body', 'Health & Symptoms'],
    'friendship': ['Making Friends', 'Conversations with Friends', 'Friendship & Support'],
}

def seed_subcategories(apps, schema_editor):
    Category = apps.get_model('teacher', 'VocabularyCategory')
    SentenceCategory = apps.get_model('teacher', 'SentenceCategory')
    Subcategory = apps.get_model('teacher', 'LearningSubcategory')
    for kind, model, mapping in (
        ('vocabulary', Category, VOCABULARY),
        ('sentence', SentenceCategory, SENTENCE),
    ):
        for category in model.objects.all():
            key = category.category_name.strip().lower()
            for name in mapping.get(key, []):
                Subcategory.objects.get_or_create(
                    material_type=kind,
                    category_id_value=category.pk,
                    name=name,
                )

class Migration(migrations.Migration):
    dependencies = [('teacher', '0055_material_subcategory_fields')]
    operations = [migrations.RunPython(seed_subcategories, migrations.RunPython.noop)]
