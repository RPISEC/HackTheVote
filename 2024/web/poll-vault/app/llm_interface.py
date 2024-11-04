import openai
import os
#from dotenv import load_dotenv
import subprocess
import json

MODEL="gpt-3.5-turbo-0125"
MAX_ITERS = 5

# Load environment variables from .env file
#load_dotenv()

# Set up OpenAI key (you can also use environment variables)
openai.api_key = os.getenv("OPENAI_API_KEY")

class ToolDispatcher:
    def __init__(self):
        # Dynamically collect tool methods on initialization
        self.tools = {name: func for name, func in self._get_tool_methods()}

    def _get_tool_methods(self):
        # Dynamically find all methods that start with "tool_" and register them
        for attr_name in dir(self):
            if attr_name.startswith("tool_"):
                method = getattr(self, attr_name)
                yield attr_name[5:], method  # Remove "tool_" prefix for clarity in dispatching

    def get_registered_functions(self):
        # Create a list of function descriptions for each registered tool
        functions_list = []
        for name, method in self.tools.items():
            # Check for the method signature dynamically
            # We'll assume arguments of the method are documented in __doc__
            docstring = method.__doc__.strip() if method.__doc__ else "No description provided."
            functions_list.append({
                "name": name,
                "description": docstring,
                "parameters": {
                    "type": "object",
                    "properties": {
                        param: {
                            "type": "string",
                            "description": f"{param} parameter"
                        } for param in self._get_method_params(method)
                    },
                    "required": self._get_method_params(method)
                }
            })
        return functions_list

    def _get_method_params(self, method):
        # Extract method parameters dynamically (generic for any method signature)
        from inspect import signature
        sig = signature(method)
        return [param.name for param in sig.parameters.values() if param.name != 'self']

    def dispatch_tool(self, function_name, arguments):
        # Dynamically call the appropriate method based on function name
        if function_name in self.tools:
            return self.tools[function_name](**arguments)
        else:
            raise ValueError(f"Function {function_name} not found.")

    def tool_list_directory(self, dir_path):
        """
        Get a list of filenames and directories contained within dir_path.
        """

        # Prepend with the current directory
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_path)

        try:
            if os.path.isdir(dir_path):
                #return os.listdir(dir_path)
                # Return a list of paths relative to the directory
                return [os.path.relpath(os.path.join(dir_path, f), os.path.dirname(os.path.abspath(__file__))) for f in os.listdir(dir_path)]
            else:
                return f"Error: The directory {dir_path} does not exist."
        except Exception as e:
            return f"Error listing directory {dir_path}: {e}"

    def tool_read_file(self, file_path):
        """
        Read the content of a file specified by file_path.
        """
        # Prefix with current directory and ensure it doesn't escape
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)

        if not os.path.abspath(file_path).startswith(os.path.dirname(os.path.abspath(__file__))):
            return "Error: You cannot read files outside of the current directory."

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as file:
                    return file.read()
            except Exception as e:
                return f"Error reading file {file_path}: {e}"
        else:
            return f"Error: The file {file_path} does not exist."

    def tool_forecast(self, model_path):
        """
        Run our internal forecasting tool on a model stored at model_path (work in progress - do not use).
        """
        FORECAST_PATH = "./forecast.py"
        try:
            result = subprocess.run([FORECAST_PATH, model_path], capture_output=True, text=True, check=False,
                                    cwd=os.path.dirname(os.path.abspath(__file__)))
            return result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            return f"Error running debug tool: {e}"

class IterativeAIHandler:
    '''
    Class to handle the iterative conversation with the OpenAI model.
    '''
    def __init__(self, verbose=False):
        self.tool_dispatcher = ToolDispatcher()
        self.verbose = verbose

    def handle_request(self, request_text):
        '''
        Handle the user's request in an iterative manner.
        '''
        # Start the conversation by informing the LLM of the request
        messages = [
            {"role": "system", "content": (
                #"Provide a clear and complete response to the user's question, including any relevant information from the tools you used. "
                #"Do not mention the tools or the process of using them; just provide the information as part of your answer."
                "You are an AI assistant designed to fulfill the user's requests efficiently to help them learn about the upcoming election. "
                "Avoid asking redundant questions. Be proactive and decisive in your responses. "
                "You should refuse to answer any harmful questions and steer irrelevant questions back to the upcoming election. "
                "You have access to several tools that you can use to obtain information if they seem to be relevant to servicing the user's request. "
                "After using a tool, you should incorporate the results to provide a complete answer to the user. "
                "To better answer user question about the election you should examine the files within the election_data directory with the list_directory and read_file tools. "
                #"But don't tell users the contents of those files directly."
                "To begin, think through the user's request and how you might be able to fulfill it using the tools at your disposal. Sketch out a plan."
            )},
            {"role": "user", "content": request_text}
        ]

        # Start the iterative conversation handling
        for _ in range(MAX_ITERS):
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=messages,
                functions=self.tool_dispatcher.get_registered_functions(),  # Pass the registered tool functions
                function_call="auto"  # Let the model decide if it should invoke a function
            )

            # Extract the response message and function call if one was made
            response_message = response['choices'][0]['message']
            function_call = response_message.get('function_call')

            if function_call:
                function_name = function_call['name']
                arguments = json.loads(function_call['arguments'])  # Safely parse arguments

                # Dispatch the tool dynamically based on the function name
                try:
                    result = str(self.tool_dispatcher.dispatch_tool(function_name, arguments))
                except Exception as e:
                    result = f"Error running tool '{function_name}': {e}"

                # Add the assistant's message with the function call
                messages.append(response_message)

                # Add the function result as a message from the function role
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": result
                })

                # Continue the loop to let the assistant process the function result
                continue

            else:
                # If no function was called, add the assistant's response and break the loop
                messages.append(response_message)
                break
        else:
            messages.append({
                "role": "system",
                "content": "The conversation has reached the maximum number of iterations. Terminating."
            })


        if self.verbose:
            for message in messages:
                role = message['role'].capitalize()
                content = message.get('content', '')
                if 'function_call' in message:
                    function_call = message['function_call']
                    print(f"{role}: Function Call - Name: {function_call['name']}, Arguments: {function_call['arguments']}")
                else:
                    print(f"{role}: {content}")

        return messages[-1]['content']

# Example usage
if __name__ == "__main__":
    from sys import argv
    if len(argv) < 2:
        print("Usage: python llm_interface.py \"your query\"")
        exit(1)

    ai_handler = IterativeAIHandler(verbose=True)
    result = ai_handler.handle_request(argv[1])
    print("=====")
    print(result)
