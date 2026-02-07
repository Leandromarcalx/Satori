# test_classifier.py
"""Test script to validate the enhanced classifier with known examples."""

from src.enhanced_classifier import classify_content

# Test cases with expected results
TEST_CASES = [
    {
        "name": "Restaurant Review - São Paulo restaurants",
        "text": """10 melhores restaurantes em São Paulo que a gente foi em 2025. 
                  Começando com o quesito Ramen, o Jojo Ramin é fortíssimo. 
                  O Indiana, o Currys muito bem servido. No quesito hamburgão o Osnir arregaça.""",
        "expected": True,
        "reason": "Clear restaurant review with multiple restaurant names and food items"
    },
    {
        "name": "Song Lyrics - Ameno",
        "text": "Dori me, in terrimo ajapare, Dori me, ameno, ameno, lanzirei, lanzirei mo, Dori me",
        "expected": False,
        "reason": "Song lyrics, not food-related"
    },
    {
        "name": "Cultural Advice - Brazilian Woman",
        "text": """Somae é brasileira, então você precisa saber algumas coisas, 
                  lição 1, ela fala alto e ela fala rápido, isso não significa que ela está brigando contigo, 
                  é só o jeito dela falar. Lissão número 2. Ela está certa. Ela sempre está certa.""",
        "expected": False,
        "reason": "Cultural/relationship advice, not food-related"
    },
    {
        "name": "Nutrition Discussion - Whey vs Milk Powder",
        "text": """Whey protein comparado com leite em pó. O objetivo do Whey sempre foi 
                  retirar o máximo de gorduras e carboidratos e manter uma concentração altíssima de proteína. 
                  É uma forma de você consumir mais proteína no seu dia.""",
        "expected": False,
        "reason": "Nutrition/supplement discussion without restaurant context"
    },
    {
        "name": "Clothing Content",
        "text": "T-wear, shorts, skirts, eyewear, t-shirts, jeez, deer, captain",
        "expected": False,
        "reason": "Fashion/clothing content"
    },
    {
        "name": "Generic Thanks",
        "text": "Thank you for watching!",
        "expected": False,
        "reason": "Generic video ending"
    },
    {
        "name": "Restaurant with Location",
        "text": """Visitamos um restaurante incrível no Bom Retiro, 
                  espetinho coreano que surpreendeu pelos temperos e as suculências da carne. 
                  Recomendo muito!""",
        "expected": True,
        "reason": "Restaurant review with location and recommendation"
    },
    {
        "name": "Home Cooking Recipe",
        "text": """Receita de bolo de chocolate caseiro. 
                  Ingredientes: farinha, açúcar, ovos, chocolate. 
                  Modo de preparo: misture tudo e leve ao forno.""",
        "expected": True,  # Should be True if include_cooking=True
        "reason": "Home cooking recipe"
    },
]

def run_tests():
    """Run all test cases and display results."""
    print("=" * 80)
    print("ENHANCED CLASSIFIER TEST SUITE")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {i}: {test['name']}")
        print(f"{'─' * 80}")
        print(f"Text: {test['text'][:100]}...")
        print(f"Expected: {'✅ Food-Related' if test['expected'] else '❌ Not Food-Related'}")
        print(f"Reason: {test['reason']}")
        print()
        
        # Classify with default settings (include_cooking=True, include_nutrition=False)
        result = classify_content(test['text'])
        
        # Check if result matches expected
        is_correct = result['is_food_related'] == test['expected']
        
        if is_correct:
            print(f"Result: ✅ PASS")
            passed += 1
        else:
            print(f"Result: ❌ FAIL")
            failed += 1
        
        # Display classification details
        print(f"\nClassification Details:")
        print(f"  Category: {result['category']}")
        print(f"  Confidence: {result['confidence']:.3f}")
        if 'ai_category' in result:
            print(f"  AI Category: {result['ai_category']}")
        print(f"  Reasoning: {result['reasoning']}")
        
        if not is_correct:
            print(f"\n  ⚠️  Expected: {test['expected']}, Got: {result['is_food_related']}")
    
    # Summary
    print(f"\n{'=' * 80}")
    print(f"TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Tests: {len(TEST_CASES)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(TEST_CASES)*100):.1f}%")
    print(f"{'=' * 80}\n")
    
    return passed, failed

if __name__ == "__main__":
    run_tests()
