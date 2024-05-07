from flask import (Flask, render_template, request, 
    redirect, session, jsonify, Response, url_for)
import sqlite3, json
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = 'd0a44f6fd56eb95da9a7ee692fdf8d49'
app.permanent_session_lifetime = timedelta(days=7)

def is_authenticated():
    return session.get('logged_in')

@app.route('/')
def home():
    context = {
        'logged_in': session.get('logged_in', False),
        'username': session.get('username', None)
    }
    conn = sqlite3.connect('debate.sqlite') 
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute('SELECT * FROM topic ORDER BY creationTime DESC')
    topics = [dict(row) for row in cursor.fetchall()]
    
    conn.close()

    context['topics'] = topics

    print("Topics retrieved from database:", topics)


    return render_template('home.html', context=context)

def check_username(username):
    try:
        connection = sqlite3.connect('debate.sqlite')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM user WHERE userName = ?', (username,))
        user = cursor.fetchone()
        return user is not None
    finally:
        connection.close()


def register_user(username, password):
    connection = None  
    try:
        if check_username(username):
            return False  

        connection = sqlite3.connect('debate.sqlite')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO user (userName, passwordHash) VALUES (?, ?)', (username, password))
        connection.commit()
        return True  
    except sqlite3.IntegrityError as e:
        print(f"Error inserting user '{username}': {e}")
        return False  
    finally:
        if connection:
            connection.close()  



@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if 'username' in session:
            return jsonify({'status': 200, 'message': 'User already logged in'}), 200

        if register_user(username, password):
            session['username'] = username
            session['logged_in'] = True
            return jsonify({'status': 200, 'username': username}), 200
        else:
            return jsonify({'status': 400, 'message': 'Username already exists'}), 400
    else:
        return render_template('register.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    context = {}
    if 'logged_in' in session:
        context['username'] = session['username']
        context['logged_in'] = session['logged_in']
        return render_template('profile.html', context=context)
    else:
        return redirect('/login')
    

def validate_login(username, password):
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
    user = cursor.fetchone()
    connection.close()

    if user and user[2] == password:
        return True
    return False


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if 'username' in session:
        return jsonify({'status': 200, 'message': 'User already logged in'}), 200

    if validate_login(username, password):
        session.permanent = True
        session['username'] = username
        session['logged_in'] = True
        return jsonify({'status': 200, 'username': username}), 200
    else:
        return jsonify({'status': 400, 'message': 'Invalid username or password'}), 400

#CREATE TOPIC
@app.route('/create_topic', methods=['POST'])
def create_topic():
    topic_name = request.form['topicName']
    posting_user = session.get('username')
    creation_time = datetime.now().strftime("%d/%m/%Y, %H:%M")
 
    try:
        connection = sqlite3.connect('debate.sqlite')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO topic (topicName, postingUser, creationTime) VALUES (?, ?, ?);
        ''', (topic_name, posting_user, creation_time))
        topic_id = cursor.lastrowid
        connection.commit()
        connection.close()

        return jsonify({"success": True, "message": "Topic has been created successfully", "topicName": topic_name, "postingUser": posting_user, "creationTime": creation_time, "topicID": topic_id})
    except Exception as e:
        return f"An error occurred while creating the topic: {e}"


@app.route('/topic/<int:topicId>')
def topic(topicId):
    try:
        with sqlite3.connect('debate.sqlite') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM topic WHERE topicID = ?', (topicId,))
            topic = cursor.fetchone()
            if topic is None:
                return "Topic not found", 404
            
            topic_data = {'topicID': topic[0], 'topicName': topic[1]}
            context = {
                'topic_data': topic_data,
                'logged_in': session.get('logged_in', False),
                'username': session.get('username', None)
            }
        
            cursor.execute('''
                SELECT c.claimID, c.topic, c.postingUser, c.creationTime, COALESCE(MAX(r.creationTime), c.creationTime) AS updateTime, c.claimHeader, c.text, ct.claimRelType
                FROM claim c
                LEFT JOIN replyToClaim rc ON c.claimID = rc.claim
                LEFT JOIN replyText r ON rc.reply = r.replyTextID
                LEFT JOIN claimToClaimType ct ON ct.claimRelTypeID = (SELECT claimRelType FROM claimToClaim WHERE first = c.claimID OR second = c.claimID LIMIT 1)
                WHERE c.topic = ?
                GROUP BY c.claimID, c.topic, c.postingUser, c.creationTime, c.claimHeader, c.text, ct.claimRelType
                ORDER BY updateTime DESC
            ''', (topicId,))

            claims = cursor.fetchall()

            claim_data_list = []
            for claim in claims:
                cursor.execute('''
                    SELECT cc.second, cc.claimRelType, c.claimHeader
                    FROM claimToClaim cc
                    JOIN claim c ON cc.second = c.claimID
                    WHERE cc.first = ?
                ''', (claim[0],))
                related_claims = cursor.fetchall()

                related_claims_list = [{
                    'claimID': rel[0],
                    'relation': rel[1],
                    'claimHeader': rel[2]
                } for rel in related_claims]

                claim_data = {
                    'claimID': claim[0],
                    'topic': claim[1],
                    'postingUser': claim[2],
                    'creationTime': claim[3],
                    'updateTime': claim[4],
                    'claimHeader': claim[5],
                    'text': claim[6],
                    'claimType': claim[7] or "Unknown Type",
                    'relatedClaims': related_claims_list
                }
                claim_data_list.append(claim_data)
            related_claims_json = json.dumps(claim_data_list)
            context['claims'] = claim_data_list

            return render_template('topic.html', context=context, related_claims_json=related_claims_json)

    except Exception as e:
        return f"An error occurred while fetching topic: {e}"



def get_claim_header(claim_id):
    with sqlite3.connect('debate.sqlite') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT claimHeader FROM claim WHERE claimID = ?', (claim_id,))
        result = cursor.fetchone()
        return result[0] if result else 'Unknown'


def get_claim_header(claim_id):
    with sqlite3.connect('debate.sqlite') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT claimHeader FROM claim WHERE claimID = ?', (claim_id,))
        result = cursor.fetchone()
        return result[0] if result else 'Unknown'

    


@app.route('/create_claim', methods=['POST'])
def create_claim():
    if request.method == 'POST':
        try:
            topic_id = request.form.get('topic_id')
            text = request.form.get('text')
            claim_header = request.form.get('claimHeader')
            relationship_type = request.form.get('relationshipType') 
            related_claims = request.form.getlist('relatedClaims[]')
            posting_user = session.get('username')
            creation_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

            if not topic_id or not text:
                return jsonify({"success": False, "message": "Topic ID and text are required"}), 400

            with sqlite3.connect('debate.sqlite') as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT INTO claim (topic, postingUser, text, creationTime, updateTime, claimHeader) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (topic_id, posting_user, text, creation_time, creation_time, claim_header))
                new_claim_id = cursor.lastrowid

                for related_claim_id in related_claims:
                    cursor.execute('''
                        INSERT INTO claimToClaim (first, second, claimRelType) 
                        VALUES (?, ?, ?)
                    ''', (new_claim_id, related_claim_id, relationship_type))

                connection.commit()

            related_claims_data = []
            for related_claim_id in related_claims:
                cursor.execute('''
                    SELECT c.claimHeader, cc.claimRelType
                    FROM claim c
                    JOIN claimToClaim cc ON cc.second = c.claimID
                    WHERE c.claimID = ?
                ''', (related_claim_id,))
                related = cursor.fetchone()
                if related:
                    claim_header, relationship_type_id = related
                    mapped_type = map_claim_type(str(relationship_type_id))
                    related_claims_data.append({
                        'claimID': related_claim_id,
                        'claimHeader': claim_header,
                        'claimType': mapped_type  
                    })

            return jsonify({
                "success": True,
                "claimID": new_claim_id,
                "claimHeader": claim_header,
                "creationTime": creation_time,
                "updateTime": creation_time,
                "postingUser": posting_user,
                "text": text,
                "claimType": map_claim_type(relationship_type), 
                "relatedClaims": related_claims_data
            })

        except Exception as e:
            return jsonify({"success": False, "message": f"An error occurred while creating the claim: {e}"}), 500


def map_reply_to_reply_type(reply_type_id):
    reply_to_reply_types = {
        '1': "Evidence",
        '2': "Support",
        '3': "Rebuttal"
    }
    reply_type_str = str(reply_type_id)
    return reply_to_reply_types.get(reply_type_str, "Unknown Type")


def map_reply_type(reply_type):
    types = {
        '1': "Clarification",
        '2': "Supporting Argument",
        '3': "Counterargument"
    }
    return types.get(reply_type, "Unknown Type")  

def map_claim_type(claim_type_id):
    print("Received claim_type_id:", claim_type_id)  
    claim_types = {
        '1': "Opposed",
        '2': "Equivalent"
    }
    return claim_types.get(str(claim_type_id), "Unknown Type")  


@app.route('/create_reply_to_claim/<int:claim_id>', methods=['POST'])
def create_reply_to_claim(claim_id):
    reply_text = request.form.get('replyText')
    reply_type = request.form.get('replyType')
    posting_user = session.get('username')
    creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not reply_type or not reply_text:
        return jsonify({"success": False, "message": "Reply Text and Reply-to-Claim Relationship Type are required"}), 400

    try:
        with sqlite3.connect('debate.sqlite') as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO replyText (postingUser, creationTime, text) VALUES (?, ?, ?)', (posting_user, creation_time, reply_text))
            reply_text_id = cursor.lastrowid
            cursor.execute('INSERT INTO replyToClaim (reply, claim, replyToClaimRelType) VALUES (?, ?, ?)', (reply_text_id, claim_id, reply_type))
            cursor.execute('UPDATE claim SET updateTime = ? WHERE claimID = ?', (update_time, claim_id))
            connection.commit()

            mapped_reply_type = map_reply_type(reply_type)
            
            return jsonify({
                "success": True,
                "message": "Reply created successfully",
                 "replyID": reply_text_id,
                "replyText": reply_text,
                "replyType": mapped_reply_type, 
                "postingUser": posting_user,
                "creationTime": creation_time
            })

    except sqlite3.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/claim/<int:claim_id>')
def view_claim(claim_id):
    try:
        with sqlite3.connect('debate.sqlite') as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT c.*, t.claimRelType
                FROM claim AS c
                LEFT JOIN claimToClaim AS cc ON c.claimID = cc.first OR c.claimID = cc.second
                LEFT JOIN claimToClaimType AS t ON cc.claimRelType = t.claimRelTypeID
                WHERE c.claimID = ?
            """, (claim_id,))
            claim_data = cursor.fetchone()
            
            if claim_data is None:
                return "Claim not found", 404

            claim = {
                'claimID': claim_data[0],
                'topic': claim_data[1],
                'postingUser': claim_data[2],
                'creationTime': claim_data[3],
                'updateTime': claim_data[4],
                'claimHeader': claim_data[5],
                'text': claim_data[6],
            }
            
            claim_type = map_claim_type(claim_data[7]) if claim_data[7] else "Unknown Type"

            cursor.execute("""
                SELECT r.replyToClaimID, r.reply, r.claim, r.replyToClaimRelType, t.text, t.postingUser, t.creationTime,
                       (SELECT COUNT(*) FROM replyToReply WHERE parent = r.reply) AS numReplies
                FROM replyToClaim AS r
                JOIN replyText AS t ON r.reply = t.replyTextID
                WHERE r.claim = ?
                ORDER BY t.creationTime ASC
            """, (claim_id,))
            replies = cursor.fetchall()

            replies_data = []
            for reply in replies:
                cursor.execute("""
                SELECT rr.replyToReplyID, rr.parent, rr.replyToReplyRelType, rt.text, rt.postingUser, rt.creationTime
                FROM replyToReply AS rr
                JOIN replyText AS rt ON rr.reply = rt.replyTextID
                WHERE rr.parent = ?
                ORDER BY rt.creationTime DESC
            """, (reply[0],))
                sub_replies = cursor.fetchall()

                sub_replies_data = []
                for sub_reply in sub_replies:
                    sub_replies_data.append({
                        'replyToReplyID': sub_reply[0],
                        'parent': sub_reply[1],
                        'replyText': sub_reply[3],
                        'postingUser': sub_reply[4],
                        'creationTime': sub_reply[5],
                        'replyToReplyRelType': map_reply_to_reply_type(sub_reply[2])
                    })

                replies_data.append({
                    'replyToClaimID': reply[0],
                    'reply': reply[1],
                    'claim': reply[2],
                    'replyToClaimRelType': map_reply_type(str(reply[3])),
                    'replyText': reply[4],
                    'postingUser': reply[5],
                    'creationTime': reply[6],
                    'numReplies': reply[7],
                    'subReplies': sub_replies_data,
                })
    
            context = {
                'claim': claim,
                'claimType': claim_type,
                'replies': replies_data,
                'logged_in': session.get('logged_in', False),
                'username': session.get('username', None)
            }
            return render_template('claim.html', context=context)
    except Exception as e:
        return f"An error occurred: {e}"


@app.route('/create_reply_to_reply/<int:parent_reply_id>', methods=['POST'])
def create_reply_to_reply(parent_reply_id):
    try:
        reply_text = request.form['replyText']
        reply_type_id = request.form['replyToReplyType']
        posting_user = session.get('username')
        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:")

        if not reply_type_id or not reply_text:
            return jsonify({"success": False, "message": "Reply Text and Reply Type are required"}), 400

        with sqlite3.connect('debate.sqlite') as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO replyText (postingUser, creationTime, text) VALUES (?, ?, ?)', 
                           (posting_user, creation_time, reply_text))
            connection.commit()

            reply_text_id = cursor.lastrowid

            cursor.execute('INSERT INTO replyToReply (reply, parent, replyToReplyRelType) VALUES (?, ?, ?)', 
                           (reply_text_id, parent_reply_id, reply_type_id))
            connection.commit()
            cursor.execute("""
            SELECT rr.replyToReplyID, rr.parent, rr.replyToReplyRelType, rt.text, rt.postingUser, rt.creationTime
            FROM replyToReply AS rr
            JOIN replyText AS rt ON rr.reply = rt.replyTextID
            WHERE rr.parent = ? AND rt.replyTextID = ?
            """, (parent_reply_id, reply_text_id))
            new_reply = cursor.fetchone()

            if new_reply:
                response_data = {
                    "replyToReplyID": new_reply[0],
                    "parent": new_reply[1],
                    "replyToReplyRelType": map_reply_to_reply_type(new_reply[2]),
                    "replyText": new_reply[3],
                    "postingUser": posting_user,
                    "creationTime": creation_time
                }
                return jsonify({
                    "success": True,
                    "message": "Reply to reply created successfully",
                    "newReply": response_data
                })
            else:
                return jsonify({"success": False, "message": "Failed to fetch the new reply"}), 400

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
