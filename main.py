import os, argparse, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from prompts import system_prompt
from call_function import available_functions
from call_function import call_function


def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")
    
    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")
    
    generate_content(client, messages, args.verbose)


def generate_content(client, messages, verbose):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=messages, 
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt
            ),
        )
        
        if not response.usage_metadata:
            raise RuntimeError("Gemini API response appears to be malformed")
        
        if verbose:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        
        if not response.function_calls:
            print("Response:")
            print(response.text)
            return
        
        function_results = []
        for function_call in response.function_calls:
            args = dict(function_call.args or {})
            # if function_call.name == "get_files_info" and "directory" not in args:
            #     args["directory"] = "."
            # print(f"Calling function: {function_call.name}({args})")
            function_call_result = call_function(function_call, verbose)
            if not function_call_result.parts:
                raise Exception("Empty parts")
            if not function_call_result.parts[0].function_response:
                raise Exception("Empty function part response")
            if not function_call_result.parts[0].function_response.response:
                raise Exception("Empty function response")
            function_results.append(function_call_result.parts[0])
            if verbose:
                print(f"-> {function_call_result.parts[0].function_response.response.result}")
    except ClientError as e:
        if e.code == 429:
            print(f"Error resource exhausted (429): {e.message}")
            sys.exit(0)  # Esce con successo
        raise e

if __name__ == "__main__":
    main()
