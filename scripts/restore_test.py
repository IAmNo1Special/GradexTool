import json
import os

brain_dir = r'C:\Users\ivmno\.gemini\antigravity\brain'
found = False

for conv_id in os.listdir(brain_dir):
    transcript_path = os.path.join(brain_dir, conv_id, '.system_generated', 'logs', 'transcript_full.jsonl')
    if os.path.exists(transcript_path):
        # Read the lines in reverse or just keep track of the LAST one found to get the most recent valid backup
        latest_content = None
        with open(transcript_path, encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if 'tool_calls' in data:
                        for call in data['tool_calls']:
                            if call['function'] == 'default_api:write_to_file':
                                args = call['arguments']
                                if 'TargetFile' in args and args['TargetFile'].endswith('test_hunting.py'):
                                    if 'CodeContent' in args:
                                        latest_content = args['CodeContent']
                except Exception:
                    pass

        if latest_content:
            print(f'Found backup in {conv_id}!')
            with open(r'f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py', 'w', encoding='utf-8') as out:
                out.write(latest_content)
            found = True
            print('Restored from write_to_file!')
            break

print('Done!')
