import threading
import cv2 as cv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time  # Import the time module

def interact_with_youtube(driver):
    try:
        # Navigate to YouTube login page
        driver.get("https://accounts.google.com/signin/v2/identifier?service=youtube")

        # Wait for the email field to be present and enter email
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        )
        email_field.send_keys("sentimentalanalysis7777@gmail.com")  # Replace with your email
        email_field.send_keys(Keys.RETURN)

        # Wait for the password field to be clickable and enter password using XPath
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
        )
        password_field = driver.find_element(
            By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'
        )
        password_field.send_keys("Sentimentalanalysis123")  # Replace with your password
        password_field.send_keys(Keys.RETURN)

        time.sleep(10)

        # Navigate to the new YouTube link
        driver.get("https://www.youtube.com")  # Replace with the desired YouTube URL
        driver.maximize_window()
        wait = WebDriverWait(driver, 15)


        reacted = False  # Flag to track if the video has been liked

        while True:
            try:
                # Get video playing status and current time
                video_info = get_video_playing_info(driver)
                is_playing = video_info['isPlaying']
                current_time = video_info['currentTime']
                
                if is_playing and not reacted and current_time >= 60:  # Check if video has been playing for 1 minute
                    video_playing_event.set()  # Signal that video is playing

                    # API CALLING HERE BEFORE LIKE AND DISLIKE  
                    
                    # Wait for the like button to be clickable and click it only if not liked
                    like_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "yt-spec-button-shape-next") and @aria-label[contains(., "like this video")]]')))
                    like_button.click()
                    print("Liked")
                    
                    reacted = True  # Set flag to True after liking the video

                elif not is_playing:
                    video_playing_event.clear()  # Signal that video is not playing
                    reacted = False  # Reset the flag if video is paused or stopped

                # Debugging print statement
                print(f"Video Playing: {is_playing}, Current Time: {current_time}, Reacted: {reacted}")

                time.sleep(1)  # Check the status every second
            except Exception as e:
                print(f"An error occurred: {e}")


    except Exception as e:
        print(f"An error occurred: {e}")



#CHECK TIME OF VIDEO PLAYING
def get_video_playing_info(driver):
    script = """
    var video = document.querySelector('video');
    if (video) {
        return {
            isPlaying: !video.paused && !video.ended && video.currentTime > 0,
            currentTime: video.currentTime
        };
    }
    return {isPlaying: false, currentTime: 0};
    """
    return driver.execute_script(script)


#CHECK IF VIDEO IS PLAYING OR NOT 
def is_video_playing(driver):
    script = """
    var video = document.querySelector('video');
    if (video) {
        return !video.paused && !video.ended && video.currentTime > 0;
    }
    return false;
    """
    return driver.execute_script(script)

def show_ip_camera_stream():
    ip_camera_url = 'http://192.168.1.114:8080/video'  # or 'rtsp://<IP>:<port>/path'
    capture_interval = 5  # seconds
    capture_file = 'captures/image.png'  # Single file to save the latest capture

    # Create the captures folder if it doesn't exist
    captures_folder = os.path.dirname(capture_file)
    if not os.path.exists(captures_folder):
        os.makedirs(captures_folder)

    cap = cv.VideoCapture(ip_camera_url)
    if not cap.isOpened():
        print("Cannot open IP camera")
        return

    # Create a named window with a specific size
    cv.namedWindow('Camera Feed', cv.WINDOW_NORMAL)
    cv.resizeWindow('Camera Feed', 0, 0)  # Adjust the size as needed

    last_capture_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Show the original frame
        cv.imshow('Camera Feed', frame)

        # Check if the video is playing before capturing
        if video_playing_event.is_set():
            current_time = time.time()
            if current_time - last_capture_time >= capture_interval:
                # Overwrite the single image file
                cv.imwrite(capture_file, frame)
                print(f"Image updated as {capture_file}")
                last_capture_time = current_time


        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    # Initialize the browser driver
    driver = webdriver.Chrome()

    # Create a threading event to signal video playback status
    video_playing_event = threading.Event()

    # Create and start threads
    youtube_thread = threading.Thread(target=interact_with_youtube, args=(driver,))
    camera_thread = threading.Thread(target=show_ip_camera_stream)

    youtube_thread.start()
    # Wait a short time to ensure the browser has fully opened
    time.sleep(5)
    camera_thread.start()

    # Wait for threads to complete
    youtube_thread.join()
    camera_thread.join()

    # Close the browser driver
    driver.quit()
