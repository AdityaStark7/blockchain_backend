import time

from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from backend.blockchain.block import Block
from backend.wallet.transactions import Transaction

pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-21066bcc-bc92-11eb-8f6a-ae5fdf7280c3'
pnconfig.publish_key = 'pub-c-4fbfc9b4-d6e5-43d0-a691-a26f18cbaada'
# pubnub = PubNub(pnconfig)


CHANNELS = {
    'TEST' : 'TEST',
    'BLOCK' : 'BLOCK',
    'TRANSACTION': 'TRANSACTION'

}


class Listener(SubscribeCallback):

    def __init__(self, blockchain, transaction_pool):
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool


    def message(self, pubnub, message_object):
        print(f'\n-- Channel: {message_object.channel} | Message: {message_object.message}')

        if message_object.channel == CHANNELS['BLOCK']:
            block = Block.from_json(message_object.message)
            potential_chain = self.blockchain.chain[:]
            potential_chain.append(block)

            try:
                self.blockchain.replace_chain(potential_chain)
                self.transaction_pool.clear_blockchain_transactions(
                    self.blockchain
                )
                print('\n--Successfully replaced the local chain')
            except Exception as e:
                print(f'\n--Did not replace chain: {e}')

        elif message_object.channel == CHANNELS['TRANSACTION']:
            transaction = Transaction.from_json(message_object.message)
            self.transaction_pool.set_transaction(transaction)
            print('\n--Set the new transaction in the transaction pool')



                

class PubSub():

    def __init__(self, blockchain, transaction_pool):
        self.pubnub = PubNub(pnconfig)
        self.pubnub.subscribe().channels(CHANNELS.values()).execute()
        self.pubnub.add_listener(Listener(blockchain, transaction_pool))

    def publish(self, channel, message):
        self.pubnub.publish().channel(channel).message(message).sync()

    def broadcast_block(self, block):
        self.publish(CHANNELS['BLOCK'], block.to_json())

    def broadcast_transaction(self, transaction):
        self.publish(CHANNELS['TRANSACTION'], transaction.to_json())




def main():
    pubsub = PubSub()
    time.sleep(1)
    pubsub.publish(CHANNELS['TEST'],{'foo':'bar'})

if __name__ == '__main__':
        main()  


