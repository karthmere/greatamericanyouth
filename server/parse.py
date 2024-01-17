import json
import os
from pandas import json_normalize
from consts import REGEXES


MESSAGES = 'messages/m2.json'

def escape(string):
    if string is None:
        return ""
    return '\"' + string.replace('\"', '\"\"') + '\"'

def write_data():
    data = None
    with open(MESSAGES) as json_data:
        data = json.load(json_data)

    
    # convert from json to df
    data = json_normalize(data['messages'])
    
    # remove messages with no content
    data = data.loc[data['content'].notnull()]

    # merge names
    data['sender_name'] = data['sender_name'].replace(['Degan Nestrichal'], 'Eddie Chavez')
    data['sender_name'] = data['sender_name'].replace(['John Crispy'], 'J Cole Patt')

    # filter by phrases
    for regex in REGEXES:
        data = data.loc[~data.content.str.contains(regex)]

    # remove long messages
    data = data.loc[~(data.content.str.len() > 500)]

    # drop index number
    data.drop(["index_number"], axis=1, inplace=True)

    # reset df index to start from 0
    data.reset_index(drop=True, inplace=True)

    data['content'] = escape(data['content'])

    if os.path.exists('messages.dat'):
        os.remove('messages.dat')

    data.to_csv('messages.dat', header=None, sep="|")

def main():
    write_data()

if __name__ == '__main__':
    main()

