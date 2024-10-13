from openai import OpenAI
from django.shortcuts import render, redirect
from django.conf import settings
import weave

# Configure OpenAI API key
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@weave.op()
def get_random_object_name():
    # Make the OpenAI API call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # You can also use gpt-4 if needed
        messages=[
            {"role": "system", "content": "You are an assistant that provides names of random objects."},
            {"role": "user", "content": "Please provide the name of a random object."}
        ]
    )
    return response.choices[0].message.content.strip()

@weave.op()
def get_prompt_image(prompt):
    # Make the OpenAI API call to generate an image
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url

def home(request):
    # Get a random object name and its corresponding image
    random_object_name = get_random_object_name()
    prompt_image = get_prompt_image(random_object_name)

    # Store the random object name in the session
    request.session['random_object_name'] = random_object_name

    # Render the homepage with the random object name and its image
    return render(request, 'pictionai_app/index.html', {
        'random_object_name': random_object_name,
        'prompt_image': prompt_image
    })

def submit_guess(request):
    if request.method == "POST":
        user_guess = request.POST.get('user_guess')

        # Retrieve the original prompt (random object name) from the session
        original_prompt = request.session.get('random_object_name')

        # Send the original prompt and the user guess to OpenAI for judgment
        judgment = get_judgment(original_prompt, user_guess)

        # Store the judgment in the session
        request.session['judgment'] = judgment

        # Redirect to the result page
        return redirect('result')

@weave.op()
def get_judgment(original_prompt, user_guess):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant judging how close a guess is to an original prompt."},
            {"role": "user", "content": f"The original prompt was: '{original_prompt}'. The user guessed: '{user_guess}'. Please judge how close the guess is."}
        ]
    )
    return response.choices[0].message.content.strip()

def result(request):
    # Retrieve the judgment from the session
    judgment = request.session.get('judgment', "No judgment available")

    return render(request, 'pictionai_app/result.html', {'judgment': judgment})

# Initialise the weave project
weave.init('pictionai')


