from openai import OpenAI
from django.shortcuts import render, redirect
from django.http import JsonResponse  # Added for JSON response
from django.conf import settings
import weave

# Configure OpenAI API key
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Define prompts as constants
RANDOM_OBJECT_SYSTEM_PROMPT = "You are an assistant that provides names of random objects."
RANDOM_OBJECT_USER_PROMPT = "Please provide the name of a random object, and I mean really random."

JUDGMENT_SYSTEM_PROMPT = "You are an assistant judging how close a guess is to an original prompt."
JUDGMENT_USER_PROMPT_TEMPLATE = "The original prompt was: '{original_prompt}'. The user guessed: '{user_guess}'. Please judge how close the guess is. Please provide a score from 1 to 10, with 1 being not even close and 10 being an exact match."

@weave.op()
def get_random_object_name(system_prompt: str, user_prompt: str):
    # Make the OpenAI API call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # You can also use gpt-4 if needed
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

@weave.op()
def get_prompt_image(original_prompt):
    # Make the OpenAI API call to generate an image
    response = client.images.generate(
        model="dall-e-3",
        prompt=original_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url

def home(request):
    # Render the homepage without fetching object and image yet
    return render(request, 'pictionai_app/index.html')

def get_random_object_and_image(request):
    if request.method == 'GET':
        # Get the random object and its corresponding image
        random_object_name = get_random_object_name(
            system_prompt=RANDOM_OBJECT_SYSTEM_PROMPT,
            user_prompt=RANDOM_OBJECT_USER_PROMPT
        )
        prompt_image = get_prompt_image(random_object_name)

        # Store the random object name in the session
        request.session['random_object_name'] = random_object_name

        # Return the random object name and image as JSON
        return JsonResponse({
            'random_object_name': random_object_name,
            'prompt_image': prompt_image
        })

def submit_guess(request):
    if request.method == "POST":
        user_guess = request.POST.get('user_guess')

        # Retrieve the original prompt (random object name) from the session
        original_prompt = request.session.get('random_object_name')

        # Define the user prompt for judgment
        user_prompt = JUDGMENT_USER_PROMPT_TEMPLATE.format(original_prompt=original_prompt, user_guess=user_guess)

        # Send the original prompt and the user guess to OpenAI for judgment
        judgment = get_judgment(original_prompt, user_guess, system_prompt=JUDGMENT_SYSTEM_PROMPT, user_prompt=user_prompt)

        # Store the judgment in the session
        request.session['judgment'] = judgment

        # Redirect to the result page
        return redirect('result')

@weave.op()
def get_judgment(original_prompt, user_guess, system_prompt: str, user_prompt: str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def result(request):
    judgment = request.session.get('judgment', "No judgment available")
    return render(request, 'pictionai_app/result.html', {'judgment': judgment})

# Initialize the weave project
weave.init('pictionai')
