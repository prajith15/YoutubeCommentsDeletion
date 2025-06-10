import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from detoxify import Detoxify
from textblob import TextBlob
from openpyxl import Workbook

# ===== CONFIGURATION =====
VIDEO_ID = "HWrRIMxK9IE"  # Replace with your video ID
CLIENT_SECRET_FILE = "client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
NEGATIVE_KEYWORDS = [
    "didn't like", "not good", "very bad", "boring", "worst", "terrible","don't","avoid",
    "hate", "lame", "poor", "disappointed", "waste", "nonsense", "awful","won't support","no one will help"
]

# ===== AUTHENTICATION =====
def get_authenticated_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0, prompt='consent', authorization_prompt_message='')
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

# ===== FETCH COMMENTS =====
def get_comments(youtube, video_id):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )
    while request:
        response = request.execute()
        for item in response["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            text = snippet.get("textDisplay", "")
            if text.strip():
                comments.append({
                    "id": item["id"],
                    "text": text.strip().replace("\n", " ")
                })
        request = youtube.commentThreads().list_next(request, response)
    return comments

# ===== ANALYZE + DELETE COMMENTS =====

def analyze_and_delete(youtube, comments, save_excel=True, output_file="deleted_comments_log.xlsx"):
    model = Detoxify("original")
    deleted_count = 0
    wb = Workbook()
    ws = wb.active
    ws.title = "Comment Moderation"
    ws.append(["Index", "Comment", "Toxicity", "Sentiment", "Deleted?", "Reason", "Comment ID"])

    for idx, comment in enumerate(comments, 1):
        text = comment["text"]
        comment_id = comment["id"]
        text_lower = text.lower()

        toxicity = model.predict(text).get("toxicity", 0)
        sentiment = TextBlob(text).sentiment.polarity

        should_delete = False
        reason = ""

        if toxicity >= 0.75:
            should_delete = True
            reason = "Toxicity"
        elif sentiment <= -0.5:
            should_delete = True
            reason = "Negative Sentiment"
        elif any(keyword in text_lower for keyword in NEGATIVE_KEYWORDS):
            should_delete = True
            reason = "Keyword"

        deleted = "No"
        try:
            if should_delete:
                youtube.comments().setModerationStatus(
                    id=comment_id,
                    moderationStatus="rejected"
                ).execute()
                deleted = "Yes"
                deleted_count += 1
                print(f"🗑️ Deleted: {text}")
            else:
                print(f"✅ Kept: {text}")
        except Exception as e:
            print(f"❌ Error deleting comment: {e}")
            reason = f"Error: {e}"

        # Log to Excel
        ws.append([idx, text, round(toxicity, 2), round(sentiment, 2), deleted, reason, comment_id])

    if save_excel:
        wb.save(output_file)
        print(f"\n📁 Excel log saved to '{output_file}'")

    print(f"\n✅ Process completed. Total deleted: {deleted_count}")

# ===== MAIN =====
if __name__ == "__main__":
    youtube = get_authenticated_service()
    print("🔄 Fetching comments...")
    comments = get_comments(youtube, VIDEO_ID)
    print(f"✅ Fetched {len(comments)} comments.\n")
    analyze_and_delete(youtube, comments)
