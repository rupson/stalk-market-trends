from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import matplotlib.pyplot as plt
from util import nullIfUndefined, newLineOrPipe, isHeaderLine, dataOrDefault

COLOURS = ['31;40m', '32;40m', '33;40m', '36;40m']
#  red      green    yellow   blue  #

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
TURNIP_SHEET_ID = '1Qv00dOqyjWtLx1gRoH_mi76Dgarrgyp7AtB5217PeGc'
SAMPLE_RANGE_NAME = 'Turnip_Selling!A1:D'


def printerFunctions(gsheet):
    values = gsheet.get('values', [])
    print('\033[0;35;40mDATE, PRICE, TOWN, TIME')
    for i in range(len(values)):
        if i > 0:
            print('\033[0;{0}{1}{2}'.format(
                COLOURS[i % 4], values[i],
                newLineOrPipe(i)),
                end="")
    print('\033[0;36;40m\n\n', '>>> Data by town <<<'.center(197, ' '), '\n')
    towns = []
    for each in values:
        if not isHeaderLine(each):
            town = each[2]
            if town not in towns:
                towns.append(town)
    dataByTown = []
    for each in towns:
        dataByTown.append([each])
    for i in range(len(towns)):
        for row in values:
            if row[2] == towns[i]:
                dataByTown[i].append([row[0], row[1], nullIfUndefined(row, 3)])

    for each in dataByTown:
        print('%s\n' % (each))
        print('-------------------'.center(200, ' '))
        print('')


def gsheet2df(gsheet):
    """ Converts Google sheet data to a Pandas DataFrame.
    Note: This script assumes that your data contains a header file on the first row!
    Also note that the Google API returns 'none' from empty cells - in order for the code
    below to work, you'll need to make sure your sheet doesn't contain empty cells,
    or update the code to account for such instances.
    """  # noqa: E501
    header = gsheet.get('values', [])[0]   # Assumes first line is header!
    # print(f">>>header: {header}")
    values = gsheet.get('values', [])[1:]  # Everything else is data.
    # print(f">>>values: {values}")
    if not values:
        print('No data found.')
    else:
        all_data = []
        for col_id, col_name in enumerate(header):
            column_data = []
            for row in values:
                column_data.append(dataOrDefault(row, col_id, None))
            ds = pd.Series(data=column_data, name=col_name)
            all_data.append(ds)
        df = pd.concat(all_data, axis=1)
        return df


def getGSheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'src/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TURNIP_SHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
        return Exception()
    return result


def plot(df, kind, title):
    df.plot(x="date", y="price", kind=kind, title=(title or None))
    plt.show()
    return


def parseRawDataFrame(kind, df):
    supportedKinds = ['by_town', 'default']
    if kind not in supportedKinds:
        return Exception('invalid format type')

    df['price'] = pd.to_numeric(df['price'])
    df['date'] = pd.to_datetime(
        df['date'],
        format='%d/%m/%Y',
        exact=True
    )
    if kind == 'by_town':
        melted = df.melt(id_vars=['town', 'price'])
        print(f"melted: {melted}")
        print(f"--\n{melted.info}\n--\n{melted.shape}")
        print(">>><<<")
        stacked = df.stack()
        print(f"stacked: {stacked}")
        print(f"--\n{stacked.values}\n--\n{stacked.shape}")
        # df_two = pd.DataFrame(
        #     {
        #         'Tendon': [123, 310, 100, 64],
        #         'Sandwich': [200, 100, 300, 250]
        #     },
        #     index=[1, 2, 3, 4]
        # )
        # df_two.plot.line()
    # df.info()
    return df


if __name__ == '__main__':
    gsheet = getGSheet()
    # printerFunctions(gsheet) #prints data wihtout using pandas dataframe
    df = gsheet2df(gsheet)
    # plot(df)
    print('Dataframe size = ', df.shape)
    augmented = parseRawDataFrame('by_town', df)
    plot(
        augmented,
        'scatter',
        'A graph showing price of turnips against date'  # noqa: E501
    )
    # print(df.head())
    # print(f"...\n...\n...\n{df.tail()}")
