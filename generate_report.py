import os
import pickle
import argparse
import create_results_html

def load_saved_runs(output_dir):
    """
    Load saved runs from the output directory.
    """
    saved_runs = {}
    for file in sorted(os.listdir(output_dir)):
        if file.endswith('.p'):
            try:
                one_run = pickle.load(open(os.path.join(output_dir, file), 'rb'))
                model_name = file.split("-run")[0]  # Extract the model name from the filename
                if model_name not in saved_runs:
                    saved_runs[model_name] = {}
                for test_name, (success, reason) in one_run.items():
                    if test_name not in saved_runs[model_name]:
                        saved_runs[model_name][test_name] = ([], [])
                    saved_runs[model_name][test_name][0].append(success)
                    saved_runs[model_name][test_name][1].append(reason)
            except Exception as e:
                print(f"Warning: Could not load data from file {file}: {e}")
    return saved_runs

def convert_to_color_through_yellow(value):
    value *= 255

    # Determine the stage of interpolation
    if value <= 127.5:
        # Stage 1: Red to Yellow
        red = 255
        green = int(value) + 127.5  # Green increases from 0 to 255
        blue = 127.5
    else:
        # Stage 2: Yellow to Green
        red = int(255 - (value - 127.5))  # Red decreases from 255 to 0
        green = 255
        blue = 127.5

    return red, green, blue            


def get_tags():
    """
    Each test has a description and a set of tags. This returns dictionaries
    of the format { "test_name": "description" } and { "test_name": ["tag1", "tag2"] }
    """
    descriptions = {}
    tags = {}
    for f in os.listdir("tests"):
        if not f.endswith(".py"): continue
        try:
            spec = importlib.util.spec_from_file_location(f[:-3], "tests/" + f)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except:
            continue
        if 'TAGS' in dir(module):
            test_case = [x for x in dir(module) if x.startswith("Test") and x != "TestCase"]
            for t in test_case:
                tags[f+"."+t] = module.TAGS
                descriptions[f+"."+t] = module.DESCRIPTION
    return tags, descriptions

def main():
    parser = argparse.ArgumentParser(description="Generate report from saved .p files.")
    parser.add_argument('--logdir', help='Input path for the .p files.', type=str, default='results')
    args = parser.parse_args()

    # Load the saved runs
    data = load_saved_runs(args.logdir)

    # Generate the report
    tags, descriptions = get_tags()  # Assuming these functions are defined in your codebase
    create_results_html.generate_report(data, tags, descriptions)

if __name__ == "__main__":
    main()