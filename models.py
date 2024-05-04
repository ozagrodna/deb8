
class User:
    def __init__(self, userID, userName, passwordHash, isAdmin, creationTime, lastVisit):
        self.userID = userID
        self.userName = userName
        self.passwordHash = passwordHash
        self.isAdmin = isAdmin
        self.creationTime = creationTime
        self.lastVisit = lastVisit

class Topic:
    def __init__(self, topicID, topicName, postingUser, creationTime, updateTime):
        self.topicID = topicID
        self.topicName = topicName
        self.postingUser = postingUser
        self.creationTime = creationTime
        self.updateTime = updateTime

class Claim:
    def __init__(self, claimID, topic, postingUser, creationTime, updateTime, text, claimHeader):
        self.claimID = claimID
        self.topic = topic
        self.postingUser = postingUser
        self.creationTime = creationTime
        self.updateTime = updateTime
        self.claimHeader = claimHeader
        self.text = text

class ClaimToClaimType:
    def __init__(self, claimRelTypeID, claimRelType):
        self.claimRelTypeID = claimRelTypeID
        self.claimRelType = claimRelType

class ClaimToClaim:
    def __init__(self, claimRelID, first, second, claimRelType):
        self.claimRelID = claimRelID
        self.first = first
        self.second = second
        self.claimRelType = claimRelType

class ReplyText:
    def __init__(self, replyTextID, postingUser, creationTime, text):
        self.replyTextID = replyTextID
        self.postingUser = postingUser
        self.creationTime = creationTime
        self.text = text

class ReplyToClaimType:
    def __init__(self, claimReplyTypeID, claimReplyType):
        self.claimReplyTypeID = claimReplyTypeID
        self.claimReplyType = claimReplyType

class ReplyToClaim:
    def __init__(self, replyToClaimID, reply, claim, replyToClaimRelType):
        self.replyToClaimID = replyToClaimID
        self.reply = reply
        self.claim = claim
        self.replyToClaimRelType = replyToClaimRelType

class ReplyToReplyType:
    def __init__(self, replyReplyTypeID, replyReplyType):
        self.replyReplyTypeID = replyReplyTypeID
        self.replyReplyType = replyReplyType

class ReplyToReply:
    def __init__(self, replyToReplyID, reply, parent, replyToReplyRelType):
        self.replyToReplyID = replyToReplyID
        self.reply = reply
        self.parent = parent
        self.replyToReplyRelType = replyToReplyRelType



