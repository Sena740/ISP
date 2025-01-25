import mediapipe as mp
import cv2
import random
import time
from hand_variables import *

vid = cv2.VideoCapture(0)
vid.set(3, 1500)  # Sets the width of the display
vid.set(4, 600)   # Sets the height of the display

# Initialize variables
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mphands = mp.solutions.hands
hands = mphands.Hands()

player_score = 0
computer_score = 0
countdown_started = False
countdown_start_time = None
result_display_start_time = None
result_display_duration = 3  # Display result for 3 seconds
countdown_duration = 3
choices = ["rock", "paper", "scissor"]
current_result = None

# Check if the hand is upside down
def is_hand_upside_down(wrist_y, fingertip_y):
    return wrist_y < fingertip_y

# Define the condition for Rock
def hand_rock(tc, tt, ip, it, mp, mt, rp, rt, pp, pt, wrist_y):
    if (ip < it) and (mp < mt) and (rp < rt) and (pp < pt):
        if abs(tc - tt) < 0.05: # Thumb is tucked inward
            return not is_hand_upside_down(wrist_y, it)
    return False

# Define the condition for Scissor
def hand_scissor(tc, tt, ip, it, mp, mt, rp, rt, pp, pt, wrist_y):
    if (ip > it) and (mp > mt) and (rp < rt) and (pp < pt):
        if abs(tc - tt) < 0.05: # Thumb is tucked inward
            return not is_hand_upside_down(wrist_y, it)
    return False

# Define the condition for Paper
def hand_paper(tc, tt, ip, it, mp, mt, rp, rt, pp, pt, wrist_y):
    if (ip > it) and (mp > mt) and (rp > rt) and (pp > pt):
        if abs(tc - tt) > 0.05: # Thumb is tucked outward
            return not is_hand_upside_down(wrist_y, it)
    return False

# Define the condition for Thumbs Up
def hand_ready(ti, tt, ip, it, mp, mt, rp, rt, pp, pt, wrist_y):
    if (ip < it) and (mp > mt) and (rp > rt) and (pp > pt) and (tt < wrist_y):
        if abs(ti - tt) < 0.05: # Thumb is tucked inward
            return not is_hand_upside_down(wrist_y, it)
    return False

# Determine the winner
def determine_winner(player, computer):
    global player_score, computer_score
    if player == computer:
        return "It's a tie!"
    elif (player == "rock" and computer == "scissor") or \
         (player == "scissor" and computer == "paper") or \
         (player == "paper" and computer == "rock"):
        player_score += 1
        return "Player wins!"
    else:
        computer_score += 1
        return "Computer wins!"

while True:
    ret, image = vid.read()
    if not ret:
        break

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB) # mirrors the display
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mphands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

        hn = results.multi_hand_landmarks[0]
        wrist_y = hn.landmark[WRIST].y  # 0
        tc = hn.landmark[THUMB_CMC].x  # 2
        ti = hn.landmark[THUMB_IP].x #3
        tt = hn.landmark[THUMB_TIP].x  # 4
        ip = hn.landmark[INDEX_FINGER_PIP].y #6
        it = hn.landmark[INDEX_FINGER_TIP].y #8
        mp = hn.landmark[MIDDLE_FINGER_PIP].y #10
        mt = hn.landmark[MIDDLE_FINGER_TIP].y #12
        rp = hn.landmark[RING_FINGER_PIP].y #14
        rt = hn.landmark[RING_FINGER_TIP].y #16
        pp = hn.landmark[PINKY_PIP].y #18
        pt = hn.landmark[PINKY_TIP].y #20
        txt = ""

        # Checks if the detected gesture is rock, scissors, or paper
        if(hand_rock(tc, tt, ip, it, mp, mt, rp, rt, pp, pt, wrist_y)):
            txt = "rock"
        elif(hand_scissor(tc, tt, ip, it, mp, mt, rp, rt, pp, pt, wrist_y)):
            txt = "scissor"
        elif(hand_paper(tc, tt, ip, it, mp, mt, rp, rt, pp, pt, wrist_y)):
            txt = "paper"
        elif (hand_ready(ti, tt, ip, it, mp, mt, rp, rt, pp, pt, wrist_y)):
            txt = "ready"
            if not countdown_started:
                countdown_started = True
                countdown_start_time = time.time()

        if countdown_started:
            elapsed_time = time.time() - countdown_start_time
            remaining_time = max(0, countdown_duration - elapsed_time)
            # Might require to adjust the color of the text depending on the background
            cv2.putText(image, f'Get Ready! {int(remaining_time)}', (600, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            if remaining_time <= 0:
                player_choice = txt
                computer_choice = random.choice(choices)
                current_result = f'Player: {player_choice}, Computer: {computer_choice}'
                result_message = determine_winner(player_choice, computer_choice)
                result_display_start_time = time.time()
                countdown_started = False  # Reset countdown

        # Display result for a few seconds
        # Might require to adjust the color of the text depending on the background
        if current_result and (time.time() - result_display_start_time) < result_display_duration:
            cv2.putText(image, current_result, (10, 550), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(image, result_message, (10, 590), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif current_result:
            current_result = None  # Clear the result after display duration

        x_min = min([lm.x for lm in hand_landmarks.landmark])
        y_min = min([lm.y for lm in hand_landmarks.landmark])
        x_max = max([lm.x for lm in hand_landmarks.landmark])
        y_max = max([lm.y for lm in hand_landmarks.landmark])

        h, w, _ = image.shape
        x_min = int(x_min * w)
        y_min = int(y_min * h)
        x_max = int(x_max * w)
        y_max = int(y_max * h)

        # Draws a square with a text indicating the gesture
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(image, txt, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Might require to adjust the color of the text depending on the background
    cv2.putText(image, f'Player Score: {player_score}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(image, f'Computer Score: {computer_score}', (image.shape[1] - 310, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 255), 2)

    cv2.imshow('Handtracker', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
vid.release()
cv2.destroyAllWindows()
