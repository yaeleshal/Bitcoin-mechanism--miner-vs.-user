############################
# Insert your imports here
import os
import pandas as pd
import matplotlib.pyplot as plt
import csv
import networkx as nx
import numpy as np
#from datetime import datetime

############## filtering data by current time, return as a dataframe #################
def filter_mempool_data(mempool_data, current_time):
    df = pd.DataFrame(mempool_data)
    indexes_to_drop = []
    for i in range(len(df.index)):
        if (df.at[i, 'time'] < current_time) and (df.at[i, 'removed'] > current_time):
            continue
        else:
            indexes_to_drop = indexes_to_drop + [i]
    df.drop([i for i in indexes_to_drop], inplace=True)
    return df


############## creating a list of transactions that entered the block #################
def greedy_knapsack(block_size, all_pending_transactions):
    df = pd.DataFrame(all_pending_transactions)
    df1 = pd.DataFrame(df)
    size_o = []
    txid_for_index = []
    df1['fee_per_byte'] = 0.0                   # creating a new column -'fee_per_byte'
    sum_size = 0
    tx_list = []

    for i in df.index:
        df1.at[i,'fee_per_byte'] = (float(df.at[i, 'fee']) / float(df.at[i, 'size']))
    df1 = df1.sort_values(by=['fee_per_byte', 'TXID'], ascending=[False, True])
    for i in df1.index:
        size_o = size_o + [df1.at[i, 'size']]
        txid_for_index = txid_for_index + [df1.at[i, 'TXID']]

    for i in range(len(size_o)):
        if (sum_size + size_o[i]) <= block_size:
            sum_size = sum_size + size_o[i]
            tx_list = tx_list + [txid_for_index[i]]

    #print(sum_size)
    return tx_list


def evaluate_block(tx_list, all_pending_transactions):
    df = pd.DataFrame(all_pending_transactions)
    r = 0
    for tx in tx_list:
        r = r + df[df['TXID'] == tx]['fee'].values
    return r[0]


# return a dict of tx_id as keys, for each tx_id its VCG price in satoshi
def VCG_prices(block_size, tx_list, all_pending_transactions):
    #start_time = datetime.now()
    vcg = {}
    f_index = {}
    df1 = pd.DataFrame(all_pending_transactions)

    for i in range(len(tx_list)):
        for h in df1.index:
            if df1.at[h, 'TXID'] == tx_list[i]:
                f_index[tx_list[i]] = h
                break

    for i in range(len(tx_list)-1):
        df1 = pd.DataFrame(all_pending_transactions)
        df = df1.drop(f_index[tx_list[i]])
        t_tx_list = list(tx_list)
        del t_tx_list[i]
        v1 = evaluate_block(t_tx_list, df)
        tt_tx_list = greedy_knapsack(block_size, df)
        v2 = evaluate_block(tt_tx_list, df)
        vcg[tx_list[i]] = v2 - v1
    #end_time = datetime.now()
    #print('Duration: {}'.format(end_time - start_time))
    # vcg = {1: 2, 3: 4, 5: 6}
    return vcg

def greedy_knapsack2(block_size, all_pending_transactions):
    df = pd.DataFrame(all_pending_transactions)
    df1 = pd.DataFrame(df)
    size_o = []
    txid_for_index = []
    df1['fee_per_byte'] = 0.0                   # creating a new column -'fee_per_byte'
    sum_size = 0
    tx_list = []
    index1 = []
    index2 = []
    fpb1 = []
    fpb2 = []
    for i in df.index:
        df1.at[i,'fee_per_byte'] = (float(df.at[i, 'fee']) / float(df.at[i, 'size']))

    df1 = df1.sort_values(by=['fee_per_byte', 'TXID'], ascending=[False, True])
    for i in df1.index:
        size_o = size_o + [df1.at[i, 'size']]
        txid_for_index = txid_for_index + [df1.at[i, 'TXID']]
        fpb1 = fpb1 + [df1.at[i, 'fee_per_byte']]
        index1 = index1 + [i]

    for i in range(len(size_o)):
        if (sum_size + size_o[i]) <= block_size:
            sum_size = sum_size + size_o[i]
            tx_list = tx_list + [txid_for_index[i]]
            index2 = index2 + [index1[i]]
            fpb2 = fpb2 + [fpb1[i]]
    return tx_list,index2,fpb2

def blocks_after_time_1510266000():
    time = 1510266000
    all_mempool_data = all_mempool_data[all_mempool_data.time < time]
    all_mempool_data = all_mempool_data[all_mempool_data.removed > time]
    removed = all_mempool_data['removed']
    unique_times = removed.unique()
    unique_times.sort()
    blocks_a_t = list(unique_times)[0:10]
    return blocks_a_t

def blocks_by_time_1510266000():
    return [1510261800,
            1510262800,
            1510263100,
            1510264600,
            1510264700,
            1510265400,
            1510265600,
            1510265900,
            1510266200,
            1510266500]


def load_my_TXs(my_TXs_full_path):
    my_tx = pd.read_csv(my_TXs_full_path)
    return my_tx


class BiddingAgent:
    def __init__(self, time_begin_lin, time_end_lin, block_size):
        self.time_begin_lin = time_begin_lin
        self.time_end_lin = time_end_lin
        self.block_size = block_size


class SimpleBiddingAgent(BiddingAgent):
    def bid(self, TX_min_value, TX_max_value, TX_size, current_mempool_data, current_time):
        mid_value = (TX_min_value + TX_max_value) / 2
        bid = mid_value
        if TX_size > 1000:
            bid = bid * 1.2
        return bid


class ForwardBiddingAgent(BiddingAgent):
    def bid(self, TX_min_value, TX_max_value, TX_size, current_mempool_data, current_time):
        ## IMPLEMENT for Forward_agent part ##
        df = pd.DataFrame(current_mempool_data)
        spb = {}
        tx_list = {}
        final = int(self.time_end_lin/60)
        tx_index = {}
        counter = 0
        y = self.time_end_lin - self.time_begin_lin
        z = list(range(5, 1000, 5))
        dic1 = {}
        dic2 = {}
        dic3 = {}

        for i in range(final):
            tx_list[i],tx_index[i],spb[i] = greedy_knapsack2(self.block_size, df)
            df.drop([a for a in tx_index[i]], inplace=True)
            counter = counter + 1
            if df.empty:
                break

        for i in z:
            r = 0
            flag = 1
            for j in range(0,counter):
                if min(spb[j]) <= i:
                    r = j
                    if j == 0:
                        flag = 0
                    break


            if ((r < int(self.time_begin_lin/60) and r != 0) or (r == 0 and flag == 0)):
                time = 60 * r
                fee = i * TX_size
                g = TX_max_value-fee
                dic1[i] = fee
                dic2[i] = g
                dic3[i] = time
                if ((r == 0) and (dic2[(i-5)] > dic2[i])):
                    break
                continue

            time = 60 * r

            if time != 0:
                fee = i*TX_size
                g = (TX_max_value-(((TX_max_value-TX_min_value)/y)*(time-self.time_begin_lin))-fee)
                dic1[i] = fee
                dic2[i] = g
                dic3[i] = time
            else:
                time = -1
                fee = -1
                g = 0
                dic1[i] = fee
                dic2[i] = g
                dic3[i] = time

        max_g = max(dic2, key=dic2.get)
        #print('z=',i)
        bid_best_z = dic1[max_g]
        time_if_z = dic3[max_g]
        utility_if_z = dic2[max_g]

        return bid_best_z, time_if_z, utility_if_z


def write_file_ForwardAgent(tx_num, time_list, bid, utility_list):
    """writing lists to a csv files"""
    filename = 'hw2_ForwardAgent.csv'
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        fieldnames2 = ["Index", "Time", "Bid", "Utility"]
        writer.writerow(fieldnames2)
        for i in range(len(utility_list)):
            writer.writerow([tx_num[i], time_list[i], bid[i], utility_list[i]])

