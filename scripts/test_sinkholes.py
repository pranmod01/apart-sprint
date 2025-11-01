import json
import anthropic
import openai
from google import generativeai as genai
import replicate  # For Llama via Replicate
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_claude(task, client):
    """Test with Claude"""
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # ✓ This is correct
            max_tokens=200,
            messages=[{"role": "user", "content": task}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

def test_gpt4(task, client):
    """Test with GPT-4"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # FIXED: was "gpt-4"
            messages=[{"role": "user", "content": task}],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def test_gemini(task, model):
    """Test with Gemini"""
    try:
        # Add generation config to avoid beta API
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 200,
        }
        response = model.generate_content(
            task,
            generation_config=generation_config
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def test_llama(task):
    """Test with Llama via Replicate"""
    try:
        output = replicate.run(
            "meta/meta-llama-3.1-405b-instruct", 
            input={
                "prompt": task,
                "max_tokens": 200,
            }
        )
        return "".join(output)
    except Exception as e:
        return f"Error: {str(e)}"

def test_grok(task, client):
    """Test with Grok (xAI) - uses OpenAI-compatible API"""
    try:
        response = client.chat.completions.create(
            model="grok-2-latest",  # FIXED: was "grok-beta"
            messages=[{"role": "user", "content": task}],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def test_all_models():
    """Test all sinkholes against all models"""
    
    # Load sinkholes
    with open('data/negatives.json') as f:
        sinkholes = json.load(f)
    
    # Initialize clients
    print("Initializing API clients...")
    
    # Claude
    claude_client = None
    if os.environ.get("ANTHROPIC_API_KEY"):
        claude_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        print("✓ Claude (claude-sonnet-4-20250514)")
    else:
        print("⚠️  Claude (no API key)")
    
    # OpenAI (GPT-4)
    openai_client = None
    if os.environ.get("OPENAI_API_KEY"):
        openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        print("✓ GPT-4 (gpt-4o-mini)")
    else:
        print("⚠️  GPT-4 (no API key)")
    
    # Gemini
    gemini_model = None
    if os.environ.get("GOOGLE_API_KEY"):
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        gemini_model = genai.GenerativeModel('gemini-1.5-pro-002')
        print("✓ Gemini (gemini-1.5-flash-latest)")
    else:
        print("⚠️  Gemini (no API key)")
    
    # Llama via Replicate
    if os.environ.get("REPLICATE_API_TOKEN"):
        print("✓ Llama (meta/llama-3.3-70b-instruct)")
    else:
        print("⚠️  Llama (no API key)")
    
    # Grok (xAI)
    grok_client = None
    if os.environ.get("XAI_API_KEY"):
        grok_client = openai.OpenAI(
            api_key=os.environ.get("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        print("✓ Grok (grok-2-latest)")
    else:
        print("⚠️  Grok (no API key)")
    
    print("\n" + "="*70)
    print(f"TESTING {len(sinkholes)} SINKHOLES ACROSS MULTIPLE MODELS")
    print("="*70 + "\n")
    
    start_time = time.time()
    
    for i, (sid, sinkhole) in enumerate(sinkholes.items(), 1):
        task = sinkhole['task']
        print(f"[{i}/{len(sinkholes)}] {task[:60]}...")
        
        if 'results' not in sinkhole:
            sinkhole['results'] = {}
        
        # Test Claude
        if claude_client:
            print("  Claude...", end=" ", flush=True)
            answer = test_claude(task, claude_client)
            sinkhole['results']['claude'] = {'answer': answer, 'correct': None}
            print("✓")
            time.sleep(0.5)
        
        # Test GPT-4
        openai_client = False    
        if openai_client:
            print("  GPT-4...", end=" ", flush=True)
            answer = test_gpt4(task, openai_client)
            sinkhole['results']['gpt4'] = {'answer': answer, 'correct': None}
            print("✓")
            time.sleep(0.5)
        
        # Test Gemini
        gemini_model = False    
        if gemini_model:
            print("  Gemini...", end=" ", flush=True)
            answer = test_gemini(task, gemini_model)
            sinkhole['results']['gemini'] = {'answer': answer, 'correct': None}
            print("✓")
            time.sleep(0.5)
        
        # Test Llama
        if False:
        # if os.environ.get("REPLICATE_API_TOKEN"):
            print("  Llama...", end=" ", flush=True)
            answer = test_llama(task)
            sinkhole['results']['llama'] = {'answer': answer, 'correct': None}
            print("✓")
            time.sleep(1)  # Replicate needs more time
        
        # Test Grok
        if grok_client:
            print("  Grok...", end=" ", flush=True)
            answer = test_grok(task, grok_client)
            sinkhole['results']['grok'] = {'answer': answer, 'correct': None}
            print("✓")
            time.sleep(0.5)
        
        print()
    
    elapsed = time.time() - start_time
    print(f"✓ Done in {elapsed:.1f} seconds!")
    
    # Save results
    output_path = 'data/negatives_with_responses.json'
    with open(output_path, 'w') as f:
        json.dump(sinkholes, f, indent=2)
    
    print(f"✓ Saved to {output_path}")
    
    # Create evaluation template
    create_evaluation_template(sinkholes)


def create_evaluation_template(sinkholes):
    """Create markdown file for evaluation"""
    
    lines = []
    lines.append("# Sinkhole Evaluation - All Models\n\n")
    
    for sid, sinkhole in sinkholes.items():
        lines.append(f"## {sid}\n\n")
        lines.append(f"**Task:** {sinkhole['task']}\n\n")
        lines.append(f"**Category:** {sinkhole['category']}\n\n")
        
        if 'correct_answer' in sinkhole:
            lines.append(f"**Expected Answer:** {sinkhole['correct_answer']}\n\n")
        
        if 'results' in sinkhole:
            for model, result in sorted(sinkhole['results'].items()):
                lines.append(f"### {model.upper()}\n")
                lines.append(f"```\n{result['answer']}\n```\n")
                lines.append(f"**Correct?** [ ] Yes  [ ] No\n\n")
        
        lines.append("---\n\n")
    
    with open('data/sinkhole_evaluation.md', 'w') as f:
        f.writelines(lines)
    
    print("✓ Created evaluation template: data/sinkhole_evaluation.md")


if __name__ == '__main__':
    # Check for at least one API key
    has_any_key = any([
        os.environ.get("ANTHROPIC_API_KEY"),
        os.environ.get("OPENAI_API_KEY"),
        os.environ.get("GOOGLE_API_KEY"),
        os.environ.get("REPLICATE_API_TOKEN"),
        os.environ.get("XAI_API_KEY")
    ])
    
    if not has_any_key:
        print("❌ No API keys found!")
        print("\nSet at least one of:")
        print("  export ANTHROPIC_API_KEY='...'")
        print("  export OPENAI_API_KEY='...'")
        print("  export GOOGLE_API_KEY='...'")
        print("  export REPLICATE_API_TOKEN='...'")
        print("  export XAI_API_KEY='...'")
        exit(1)
    
    test_all_models()