# -----------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# -----------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 31 July 2013
#
# Copyright 2012 Linkoping University
# -----------------------------------------------------------------------------

"""Module for the distributed mutual exclusion implementation.

This implementation is based on the second Rikard-Agravara algorithm.
The implementation should satisfy the following requests:
    --  when starting, the peer with the smallest id in the peer list
        should get the token.
    --  access to the state of each peer (dictinaries: request, token,
        and peer_list) should be protected.
    --  the implementation should gratiously handle situations when a
        peer dies unexpectedly. All exceptions comming from calling
        peers that have died, should be handled such as the rest of the
        peers in the system are still working. Whenever a peer has been
        detected as dead, the token, request, and peer_list
        dictionaries should be updated acordingly.
    --  when the peer that has the token (either TOKEN_PRESENT or
        TOKEN_HELD) quits, it should pass the token to some other peer.
    --  For simplicity, we shall not handle the case when the peer
        holding the token dies unexpectedly.

"""

from threading import Lock
import time

NO_TOKEN = 0
TOKEN_PRESENT = 1
TOKEN_HELD = 2


class DistributedLock(object):

    """Implementation of distributed mutual exclusion for a list of peers.

    Public methods:
        --  __init__(owner, peer_list)
        --  initialize()
        --  destroy()
        --  register_peer(pid)
        --  unregister_peer(pid)
        --  acquire()
        --  release()
        --  request_token(time, pid)
        --  obtain_token(token)
        --  display_status()

    """

    def __init__(self, owner, peer_list):
        self.peer_list = peer_list
        self.owner = owner
        self.time = 0
        self.token = None
        self.request = {}
        self.state = NO_TOKEN
        self.localLock = Lock()

    def _prepare(self, token):
        """Prepare the token to be sent as a JSON message.

        This step is necessary because in the JSON standard, the key to
        a dictionary must be a string whild in the token the key is
        integer.
        """
        return list(token.items())

    def _unprepare(self, token):
        """The reverse operation to the one above."""
        return dict(token)

    # Public methods

    def initialize(self):
        """ Initialize the state, request, and token dicts of the lock.

        Since the state of the distributed lock is linked with the
        number of peers among which the lock is distributed, we can
        utilize the lock of peer_list to protect the state of the
        distributed lock (strongly suggested).

        NOTE: peer_list must already be populated when this
        function is called.

        """
        print("distributedLock.initialize()")
##        self.token = dict()
##        peerIDs = self.peer_list.get_peers().keys()
##        for ID in peerIDs:
##            self.token[ID] = 0
        

    def destroy(self):
        """ The object is being destroyed.

        If we have the token (TOKEN_PRESENT or TOKEN_HELD), we must
        give it to someone else.

        """
        print("distributedLock.destroy()")
        print("I'm leaving...")
        #
        # Your code here.
        #
        

    def register_peer(self, pid):
        """Called when a new peer joins the system."""
        print("distributedLock.register_peer({})".format(pid))
        print("Someone's connecting...")
        #
        # Your code here.
        #
        

    def unregister_peer(self, pid):
        """Called when a peer leaves the system."""
        print("distributedLock.unregister_peer({})".format(pid))
        print("Someone's leaving...")
        #
        # Your code here.
        #


    """
        Acquisition scheme:
            Request token from all registered peers.
                In this RMI framework, peers will respond with an acknowledgement
                message regardless of whether they have the token.
                    If no ack is received within a timeout period, there should be
                    some exception handling.
            Wait for a peer to send the token using our obtain_token() method.
    """

    def acquire(self):
        """Called when this object tries to acquire the lock."""
        print("distributedLock.acquire()".format())
        print("Trying to acquire the lock...")

        # Increment our local timer
        self.time+=1

        for peer in self.peer_list.get_peers():
            peer.request_token(self.time,self.owner.id)

        # If we acquired the token while requesting, this will pass immediately
        while self.state == NO_TOKEN:
            time.sleep(1)


    def release(self):
        """Called when this object releases the lock."""
        print("distributedLock.release()".format())
        print("Releasing the lock...")
        
        self.state = TOKEN_PRESENT

        # Safely initiate token transfer if possible
        self._check_token()


    def request_token(self, time, pid):
        """Called when some other object requests the token from us."""
        print("distributedLock.request_token({}, {})".format(time, pid))

        # Update this client's last-requested timestamp for the other client
        self.request[pid]=time

        if self.state == TOKEN_PRESENT and self.token[pid] < self.request[pid]:
            # Safely initiate token transfer

            self._check_token()
            
            # Note that we are not necessarily going to send the token to the peer
            # that just requested it.

        return "{} acknowledging request from {}".format(self.owner.id,pid)


    def obtain_token(self, token):
        """Called when some other object is giving us the token."""
        print("distributedLock.obtain_token({})".format(token))
        print("Receiving the token...")

        if self.state is not NO_TOKEN:
            print "WARNING: peer {} has received a token when it already had one".format(self.owner.id)
        
        self.token = token

        # Update the token's last-held timestamp for this client
        self.token[self.owner.id] = self.time # TODO make sure time is increasing

        self.state = TOKEN_HELD


    def _check_token(self):
        """Called when this object checks its set of token requests in order
        to find a peer that should get the token"""
        print("distributedLock._check_token()")

        # Use Python's built-in locking (like Java's semaphore) to prevent
        # more than one of these checks from being run concurrently
        self.localLock.acquire()

        targetID = None

        # If we don't have the token or we are using it right now, we can just stop here
        if self.state == TOKEN_PRESENT:
            peer_ids = request.keys()
            gt = sorted([pid for pid in peer_ids if pid > self.owner.id])
            lt = sorted([pid for pid in peer_ids if pid < self.owner.id])

            # Check each peer in clockwise order to see if anyone wants the token
            for pid in gt + lt:
                if pid in token and self.requests[pid] > self.token[pid]:
                    targetID = pid
                    break

        if targetID is not None:
            try:
                self.state = NO_TOKEN
                self.owner.peer_list[pid].obtain_token(self.token)
            except Exception as e:
                print "ERROR: Could not send token to pid",pid
                print e

        self.localLock.release()

    def display_status(self):
        """Print the status of this peer."""
        self.localLock.acquire()
        try:
            nt = self.state == NO_TOKEN
            tp = self.state == TOKEN_PRESENT
            th = self.state == TOKEN_HELD
            print("State   :: no token      : {0}".format(nt))
            print("           token present : {0}".format(tp))
            print("           token held    : {0}".format(th))
            print("Request :: {0}".format(self.request))
            print("Token   :: {0}".format(self.token))
            print("Time    :: {0}".format(self.time))
        finally:
            self.localLock.release()
