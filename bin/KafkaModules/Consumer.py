# -*- coding: utf-8 -*-
import confluent_kafka
import Mobigen.Common.Log as Log

from confluent_kafka import KafkaException, KafkaError

class Consumer:
    """
        For generate consumer object

        Parameters
        ----------
        topic : <string>
            topic to be set

        conf : <dict>
            kafka configuration
            refer to https://kafka.apache.org/documentation/#consumerconfigs
    """
    def __init__(self, topic, conf):
        self.c = confluent_kafka.Consumer(**conf)
        self.c.subscribe([topic], on_assign=self.print_assignment)

    def print_assignment(self, consumer, partitions):
        """
            Set what call-back function do when to get message

            Parameters
            ----------
            consumer : <confluent_kafka.Consumer object>
        """
        __LOG__.Trace('Assignment: %s', partitions)

    def polling(self, timeout=1):
        """
            poll message

            Parameters
            ----------
            timeout : <int>
                timeout for polling
        """
        try:
            msg = self.c.poll(timeout)
            if msg is None:
                return None
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    __LOG__.Trace('%s [%d] reached end at offset %d' %
                                (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    #Error
                    __LOG__.Trace("Error : %s" % msg.error())
                    raise KafkaException(msg.error())
            else:
                # Proper message
                __LOG__.Trace('%s [%d] at offset %d with key %s:' %
                            (msg.topic(), msg.partition(), msg.offset(),
                            str(msg.key())))
                __LOG__.Trace(msg.value())

            return msg.value()
        except KeyboardInterrupt:
            __LOG__.Trace('Aborted by user\n')

        # Close down consumer to commit final offsets
        c.close()

