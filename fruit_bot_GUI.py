#!/usr/bin/env python3
import customtkinter as ctk
from tkinter import filedialog, BooleanVar
import tkinter as tk
from PIL import Image, ImageTk
import fruit_bot  # global variable and chat function
import requests
import io
import re
import webbrowser
from fruit_multi_object import predict_and_draw

from fruit_game import generate_sweetness_game_question
# single shot question and answer system...

'''GUI for the Fruit Bot chatbot application.'''

def open_link(event, url):
    '''Opens a given URL in the default web browser.'''
    webbrowser.open(url)

MAIN_FRAME_BG_COLOUR = "#212529"
CHAT_FRAME_BG_COLOUR = "#343a40"
INPUT_FRAME_BG_COLOUR = "#343a40"
TRANSPARENT_COLOUR = "transparent"

CHAT_BUBBLE_BG_COLOUR = "#adb5bd"
BOT_SENDER_TEXT_COLOUR = "green"
USER_SENDER_TEXT_COLOUR = "blue"
BOT_MESSAGE_TEXT_COLOUR = "#212529"
USER_MESSAGE_TEXT_COLOUR = "#212529"

ENTRY_BG_COLOUR = "#6c757d"
ENTRY_TEXT_COLOUR = "#f8f9fa"
ENTRY_PLACEHOLDER_TEXT = "Type your message here"
ENTRY_PLACEHOLDER_TEXT_COLOUR = "#adb5bd"

SEND_BUTTON_BG_COLOR = "#495057"
SEND_BUTTON_HOVER_COLOR = "#6c757d"
UPLOAD_BUTTON_BG_COLOR = "#495057"
UPLOAD_BUTTON_HOVER_COLOR = "#6c757d"

VECTOR_SWITCH_BG_ACTIVE_COLOUR = "#53484d"
VECTOR_SWITCH_STICK_ACTIVE_COLOUR = "#53484d"  
VECTOR_SWITCH_BG_INACTIVE_COLOUR = "#484d53"
VECTOR_SWITCH_STICK_INACTIVE_COLOUR = "#484d53"

# A tricky balance, it's true, Magic numbers or constants, what to do?

class FruitBotGUI:
    def __init__(self):
        '''Initialises the main GUI application and its components.'''
        self.app = ctk.CTk()
        self.app.geometry("650x700")
        self.app.resizable(False, False)
        self.app.title("Fruit Bot GUI")
        
        self.main_frame = ctk.CTkFrame(self.app, fg_color=MAIN_FRAME_BG_COLOUR)
        self.main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.chatbot_name = "Ferb"
        
        self.chat_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color=CHAT_FRAME_BG_COLOUR)
        self.chat_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.7)
        
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color=INPUT_FRAME_BG_COLOUR)
        self.input_frame.place(relx=0.05, rely=0.78, relwidth=0.9, relheight=0.17)
        
        self.entry = ctk.CTkEntry(self.input_frame,
                                  placeholder_text=ENTRY_PLACEHOLDER_TEXT,
                                  placeholder_text_color=ENTRY_PLACEHOLDER_TEXT_COLOUR,
                                  fg_color=ENTRY_BG_COLOUR,
                                  text_color=ENTRY_TEXT_COLOUR)
        self.entry.place(relx=0.02, rely=0.17, relwidth=0.70, relheight=0.5)
        self.entry.bind("<Return>", self.send_message_event)
        
        self.send_button = ctk.CTkButton(self.input_frame,
                                         text="Send",
                                         command=self.send_message,
                                         fg_color=SEND_BUTTON_BG_COLOR,
                                         hover_color=SEND_BUTTON_HOVER_COLOR)
        self.send_button.place(relx=0.74, rely=0.27, relwidth=0.24, relheight=0.4)
        
        self.upload_button = ctk.CTkButton(self.input_frame,
                                           text="Add Image",
                                           command=self.upload_image,
                                           fg_color=UPLOAD_BUTTON_BG_COLOR,
                                           hover_color=UPLOAD_BUTTON_HOVER_COLOR)
        self.upload_button.place(relx=0.02, rely=0.75, relwidth=0.96, relheight=0.2)
        
        self.switch_var = BooleanVar(value=fruit_bot.is_vectorisation_on)
        self.vec_switch = ctk.CTkSwitch(
            self.input_frame,
            text="Vec Mode",
            variable=self.switch_var,
            command=self.toggle_vectorisation,
            fg_color=VECTOR_SWITCH_BG_INACTIVE_COLOUR,
            button_color=VECTOR_SWITCH_STICK_INACTIVE_COLOUR,
            button_hover_color=VECTOR_SWITCH_STICK_INACTIVE_COLOUR,
            progress_color=VECTOR_SWITCH_STICK_INACTIVE_COLOUR,
            text_color="white"
        )
        self.vec_switch.place(relx=0.75, rely=0.04)

        self.queued_image = None
        self.queued_image_path = None
        
        # GAME GAME GAME GAME GAME GAME GAME GAME GAME
        self.game_mode = False
        self.current_game_question = None
        
        # SINGLE AND MULTIPLE TOGETHER....
        # "second option"
        self.last_prediction_generated = False

        self.app.after(3000, lambda: self.add_message(
            self.chatbot_name,
            "Welcome! My name is Ferb, the friendly fruit bot. Ask me anything fruity!",
            is_bot=True)
        )

    def add_message(self, sender, message, is_bot=True):
        '''Displays a text message in the chat area, handling URL hyperlinks and auto-scrolling.'''
        chat_width = self.chat_frame.winfo_width() if self.chat_frame.winfo_width() > 0 else 500
        bubble_max_width = int(chat_width * 0.8)
        
        container = ctk.CTkFrame(self.chat_frame, fg_color=TRANSPARENT_COLOUR)
        container.pack(fill="x", pady=2, padx=0)
        
        bubble = ctk.CTkFrame(container, fg_color=CHAT_BUBBLE_BG_COLOUR, corner_radius=8, width=bubble_max_width)
        bubble.pack(anchor="w" if is_bot else "e", padx=0)
        
        sender_text = f"{self.chatbot_name}: " if is_bot else "You: "
        text_color = BOT_SENDER_TEXT_COLOUR if is_bot else USER_SENDER_TEXT_COLOUR
        sender_label = ctk.CTkLabel(bubble, text=sender_text, text_color=text_color,
                                    font=("Helvetica", 12, "bold"), anchor="w")
        sender_label.pack(side="top", anchor="w", padx=10, pady=(0, 0))
        
        url_match = re.search(r"(https?://[^\s]+)", message)
        if url_match:
            pre_text, url, post_text = message.partition(url_match.group(0))
            if pre_text:
                pre_label = ctk.CTkLabel(bubble, text=pre_text, wraplength=bubble_max_width - 20,
                                          anchor="w", justify="left", text_color=BOT_MESSAGE_TEXT_COLOUR if is_bot else USER_MESSAGE_TEXT_COLOUR)
                pre_label.pack(side="top", anchor="w", padx=10, pady=(0, 0))
            link_label = ctk.CTkLabel(bubble, text=url, wraplength=bubble_max_width - 20,
                                       anchor="w", justify="left", text_color="blue")
            link_label.bind("<Button-1>", lambda e, link=url: webbrowser.open(link))
            link_label.pack(side="top", anchor="w", padx=10, pady=(0, 0))
            if post_text:
                post_label = ctk.CTkLabel(bubble, text=post_text, wraplength=bubble_max_width - 20,
                                          anchor="w", justify="left", text_color=BOT_MESSAGE_TEXT_COLOUR if is_bot else USER_MESSAGE_TEXT_COLOUR)
                post_label.pack(side="top", anchor="w", padx=10, pady=(0, 0))
        else:
            msg_label = ctk.CTkLabel(bubble, text=message, wraplength=bubble_max_width - 20,
                                     anchor="w", justify="left", text_color=BOT_MESSAGE_TEXT_COLOUR if is_bot else USER_MESSAGE_TEXT_COLOUR)
            msg_label.pack(side="top", anchor="w", padx=10, pady=(0, 0))
        
        self.app.update_idletasks()
        try:
            canvas = getattr(self.chat_frame, '_canvas', None)
            if canvas is None:
                canvas = getattr(self.chat_frame, '_parent_canvas', None)
            if canvas:
                canvas.update_idletasks()
                canvas.yview_moveto(1.0)
        except Exception as e:
            print("Auto-scroll error:", e)

    def add_image_to_chat(self, image_path, is_user=True):
        '''Displays an image in the chat area, performing object detection if it's a local image.'''
        try:
            if image_path.startswith("http"):
                response = requests.get(image_path)
                img = Image.open(io.BytesIO(response.content))
            else:
                img = Image.open(image_path)
                prediction_img = predict_and_draw(image_path)
                if prediction_img is not None:
                    self.last_prediction_generated = True
            chat_width = self.chat_frame.winfo_width() if self.chat_frame.winfo_width() > 0 else 500
            target_width = int(0.4 * chat_width)
            w_percent = target_width / float(img.size[0])
            target_height = int(float(img.size[1]) * w_percent)
            img = img.resize((target_width, target_height), Image.LANCZOS)
            
            ctk_img = ImageTk.PhotoImage(img)
            image_label = ctk.CTkLabel(self.chat_frame, image=ctk_img, text="")
            image_label.image = ctk_img
            
            image_label.pack(anchor="e", padx=0, pady=(2, 4))
            
            self.app.update_idletasks()
            canvas = getattr(self.chat_frame, '_canvas', None) or getattr(self.chat_frame, '_parent_canvas', None)
            if canvas:
                canvas.update_idletasks()
                canvas.yview_moveto(1.0)
        except Exception as e:
            print("Image render error:", e)

    def show_second_opinion_image(self):
        '''Displays the fruit prediction image generated by the bot in the chat.'''
        try:
            img = Image.open("fruit_prediction.png")
            chat_width = self.chat_frame.winfo_width() if self.chat_frame.winfo_width() > 0 else 500
            target_width = int(0.4 * chat_width)
            w_percent = target_width / float(img.size[0])
            target_height = int(float(img.size[1]) * w_percent)
            img = img.resize((target_width, target_height), Image.LANCZOS)
            ctk_img = ImageTk.PhotoImage(img)
            image_label = ctk.CTkLabel(self.chat_frame, image=ctk_img, text="")
            image_label.image = ctk_img
            image_label.pack(anchor="w", padx=0, pady=(2, 4))
            self.app.update_idletasks()
            canvas = getattr(self.chat_frame, '_canvas', None) or getattr(self.chat_frame, '_parent_canvas', None)
            if canvas:
                canvas.update_idletasks()
                canvas.yview_moveto(1.0)
        except Exception as e:
            print("Second opinion image error:", e)

    def upload_image(self):
        '''Prompts the user to select an image file and prepares it for bot processing.'''
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            try:
                img = Image.open(file_path)
                chat_width = self.chat_frame.winfo_width() if self.chat_frame.winfo_width() > 0 else 500
                target_width = int(0.8 * chat_width)
                w_percent = target_width / float(img.size[0])
                target_height = int(float(img.size[1]) * w_percent)
                img = img.resize((target_width, target_height), Image.LANCZOS)
                self.queued_image = ctk.CTkImage(light_image=img, dark_image=img)
                self.queued_image_path = file_path
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "what is this an image of?")
            except Exception as e:
                print("Error loading image:", e)

    def send_message_event(self, event):
        '''Handles sending a message when the Enter key is pressed.'''
        self.send_message()

    def send_message(self):
        '''Processes user input, interacts with the Fruit Bot backend, and updates the chat display.'''
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.entry.delete(0, tk.END)
        
        if self.game_mode:
            self.add_message("You", user_text, is_bot=False)
            if user_text in ["1", "2"]:
                if self.current_game_question["correct"] == "equal":
                    response = "Both options are equally sweet!"
                elif user_text == self.current_game_question["correct"]:
                    response = f"Correct! (Option 1: {self.current_game_question['overall1']:.2f}, Option 2: {self.current_game_question['overall2']:.2f})"
                else:
                    response = f"Incorrect. (Option 1: {self.current_game_question['overall1']:.2f}, Option 2: {self.current_game_question['overall2']:.2f})"
                self.add_message(self.chatbot_name, response, is_bot=True)
                self.game_mode = False
                self.current_game_question = None
                return
            else:
                self.add_message(self.chatbot_name, "Please type 1 or 2 to answer the game question.", is_bot=True)
                return

        self.add_message("You", user_text, is_bot=False)
        if user_text.lower() == "game":
            self.current_game_question = generate_sweetness_game_question()
            self.add_message(self.chatbot_name, self.current_game_question["question"], is_bot=True)
            self.game_mode = True
            return

        if user_text.lower() == "second opinion" and self.last_prediction_generated:
            self.show_second_opinion_image()
            self.last_prediction_generated = False
            return
        if self.queued_image_path:
            self.add_image_to_chat(self.queued_image_path, is_user=True)
            bot_response = fruit_bot.ferb_respond_mate(user_text, 2, image_pathway=self.queued_image_path)
            self.queued_image = None
            self.queued_image_path = None
        else:
            bot_response = fruit_bot.ferb_respond_mate(user_text, 2)
        self.add_message(self.chatbot_name, bot_response, is_bot=True)

    def toggle_vectorisation(self):
        '''Toggles the bot's response mode between AIML and vectorisation (semantic similarity).'''
        new_state = self.switch_var.get()
        fruit_bot.is_vectorisation_on = new_state
        if new_state:
            self.vec_switch.configure(
                fg_color=VECTOR_SWITCH_BG_ACTIVE_COLOUR,
                button_color=VECTOR_SWITCH_STICK_ACTIVE_COLOUR,
                button_hover_color=VECTOR_SWITCH_STICK_ACTIVE_COLOUR,
                progress_color=VECTOR_SWITCH_STICK_ACTIVE_COLOUR
            )
        else:
            self.vec_switch.configure(
                fg_color=VECTOR_SWITCH_BG_INACTIVE_COLOUR,
                button_color=VECTOR_SWITCH_STICK_INACTIVE_COLOUR,
                button_hover_color=VECTOR_SWITCH_STICK_INACTIVE_COLOUR,
                progress_color=VECTOR_SWITCH_STICK_INACTIVE_COLOUR
            )
        print("Vectorisation mode set to:", fruit_bot.is_vectorisation_on)

    def run(self):
        '''Starts the main event loop for the GUI application.'''
        self.app.mainloop()

if __name__ == "__main__":
    gui = FruitBotGUI()
    gui.run()
