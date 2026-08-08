import os

import pandas as pd
import streamlit as st
from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="For You ❤️",
    page_icon="❤️",
    layout="centered"
)

QUESTIONS_FILE = "questions.csv"
PREDICTIONS_FILE = "my_predictions.csv"
ANSWERS_FILE = "her_answers.csv"
PHOTO_FOLDER = "photos"


# ============================================================
# DATA
# ============================================================

df_questions = pd.read_csv(QUESTIONS_FILE)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "started": False,
    "current_question": 0,
    "answers": [],
    "show_results": False,
    "show_final": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def save_answer(question, answer):

    st.session_state.answers.append({
        "question_id": question["question_id"],
        "actual_answer": answer
    })

    pd.DataFrame(
        st.session_state.answers
    ).to_csv(
        ANSWERS_FILE,
        index=False
    )


def load_results():

    predictions = pd.read_csv(
        PREDICTIONS_FILE
    )

    actual_answers = pd.read_csv(
        ANSWERS_FILE
    )

    results = pd.merge(
        predictions,
        actual_answers,
        on="question_id",
        how="inner"
    )

    results["correct"] = (
        results["my_prediction"]
        == results["actual_answer"]
    )

    return results


def reset_experiment():

    st.session_state.started = True
    st.session_state.current_question = 0
    st.session_state.answers = []
    st.session_state.show_results = False
    st.session_state.show_final = False

    if os.path.exists(ANSWERS_FILE):

        os.remove(ANSWERS_FILE)

    st.rerun()


def display_photo(photo, photo_memories):

    photo_path = os.path.join(
        PHOTO_FOLDER,
        photo
    )

    try:

        image = Image.open(photo_path)

        st.image(
            image,
            use_container_width=True
        )

        memory = photo_memories.get(
            photo,
            {
                "title": os.path.splitext(photo)[0],
                "text": ""
            }
        )

        st.subheader(
            f"❤️ {memory['title']}"
        )

        if memory["text"]:

            st.caption(
                memory["text"]
            )

    except Exception:

        st.warning(
            f"Could not display {photo}"
        )


# ============================================================
# WELCOME
# ============================================================

if not st.session_state.started:

    st.write("")
    st.markdown("### 🌸   ✨   🌸")

    st.title("How well do I know you? 😊❤️")

    st.markdown(
        """
### Let's find out... 😄
"""
    )

    st.write("")

    st.markdown(
        """
🌷 &nbsp;&nbsp;&nbsp; ❤️ &nbsp;&nbsp;&nbsp; 🌷
"""
    )

    st.write("")

    if st.button(
        "✨ Start the Experiment ✨",
        use_container_width=True
    ):

        reset_experiment()


# ============================================================
# MAIN EXPERIENCE
# ============================================================

else:

    total_questions = len(df_questions)

    current_question = (
        st.session_state.current_question
    )


    # ========================================================
    # QUESTIONS
    # ========================================================

    if current_question < total_questions:

        question = df_questions.iloc[
            current_question
        ]

        st.progress(
            (current_question + 1)
            / total_questions
        )

        st.caption(
            f"Question {current_question + 1} "
            f"of {total_questions}"
        )

        st.divider()

        st.subheader(
            question["question"]
        )

        st.write("")

        col1, col2 = st.columns(2)


        with col1:

            if st.button(
                question["option_a"],
                use_container_width=True
            ):

                save_answer(
                    question,
                    question["option_a"]
                )

                st.session_state.current_question += 1

                st.rerun()


        with col2:

            if st.button(
                question["option_b"],
                use_container_width=True
            ):

                save_answer(
                    question,
                    question["option_b"]
                )

                st.session_state.current_question += 1

                st.rerun()


    # ========================================================
    # FINISHED SCREEN
    # ========================================================

    elif not st.session_state.show_results:

        st.progress(1.0)

        st.title("✨ You made it!")

        st.markdown(
            """
###  Done. 🥳

Now comes the interesting part...

**How well do you think I know you?**
"""
        )

        st.caption(
            "There's only one way to find out."
        )

        if st.button(
            "Reveal the Results",
            use_container_width=True
        ):

            st.session_state.show_results = True

            st.rerun()


    # ========================================================
    # RESULTS
    # ========================================================

    elif not st.session_state.show_final:

        results = load_results()

        accuracy = (
            results["correct"].mean()
            * 100
        )

        correct_count = int(
            results["correct"].sum()
        )

        total = len(results)


        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        st.title("The Results")

        st.metric(
            "My Score",
            f"{accuracy:.1f}%"
        )

        st.caption(
            f"{correct_count} out of "
            f"{total} predictions were correct.😊"
        )


        # ----------------------------------------------------
        # CATEGORY ANALYSIS
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "Where do I know you best?"
        )

        category_results = (
            results
            .groupby("category")["correct"]
            .mean()
            .mul(100)
            .reset_index()
        )

        for _, row in category_results.iterrows():

            score = float(
                row["correct"]
            )

            st.write(
                f"**{row['category']} — "
                f"{score:.0f}%**"
            )

            st.progress(
                int(score)
            )


        # ----------------------------------------------------
        # MISTAKES
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "Things I Got Wrong By mistake 😅"
        )

        wrong = results[
            ~results["correct"]
        ]

        if wrong.empty:

            st.success(
                "Apparently I know you perfectly. ❤️"
            )

        else:

            for _, row in wrong.iterrows():

                with st.container(
                    border=True
                ):

                    st.subheader(
                        row["question"]
                    )

                    st.write(
                        "I thought:"
                    )

                    st.error(
                        f"❌ {row['my_prediction']}"
                    )

                    st.write(
                        "But you chose:"
                    )

                    st.success(
                        f"❤️ {row['actual_answer']}"
                    )


        # ----------------------------------------------------
        # TRANSITION
        # ----------------------------------------------------

        st.divider()

        st.markdown(
            """
### But honestly...

This was never really about getting
every answer right.
And apparently, there are lot of
things about you I have yet to know.

I think that's a good. ❤️
"""
        )

        if st.button(
            "There's One More Thing...",
            use_container_width=True
        ):

            st.session_state.show_final = True

            st.rerun()


    # ========================================================
    # FINAL EXPERIENCE
    # ========================================================

    else:

        results = load_results()


        # ====================================================
        # INTRODUCTION
        # ====================================================

        st.title(
            "🎁 ..."
        )

        st.markdown(
            """
### Here's something a little more personal.😀

A very unofficial profile of you —
built from the choices you just made. 🤖🧐
"""
        )

        st.info(
            "warning! Not a scientific proven personality test...hehee "
    
        )


        # ====================================================
        # UNOFFICIAL PROFILE
        # ====================================================

        st.divider()

        dimensions = {

            "🌙 Night Owl": [
                (
                    "Morning or Night?",
                    "Night"
                )
            ],

            "🏔️ Adventure": [
                (
                    "Mountain or Beach?",
                    "Mountain"
                ),
                (
                    "Planned Trip or Spontaneous Trip?",
                    "Spontaneous"
                )
            ],

            "❤️ Romance": [
                (
                    "2 AM Deep Talk or Brunch Deep Talk?",
                    "2 AM Deep Talk"
                )
            ],

            "🧠 Emotion": [
                (
                    "Logic or Emotion?",
                    "Emotion"
                )
            ],

            "💭 Deep Connection": [
                (
                    "Talk or Listen?",
                    "Listen"
                ),
                (
                    "2 AM Deep Talk or Brunch Deep Talk?",
                    "2 AM Deep Talk"
                )
            ]
        }


        profile_scores = {}


        for dimension, rules in dimensions.items():

            matches = 0

            for question_text, desired_answer in rules:

                matching_rows = results[
                    results["question"]
                    .astype(str)
                    .str.strip()
                    == question_text.strip()
                ]

                if not matching_rows.empty:

                    actual_answer = str(
                        matching_rows.iloc[0][
                            "actual_answer"
                        ]
                    ).strip()

                    if actual_answer == desired_answer:

                        matches += 1


            profile_scores[dimension] = (
                matches / len(rules) * 100
            )


        st.subheader(
            " Extremely Unofficial Model of Your personality.😎"
        )


        for dimension, score in profile_scores.items():

            st.write(
                f"**{dimension} — "
                f"{score:.0f}%**"
            )

            st.progress(
                int(score)
            )


        # ====================================================
        # SCIENTIFIC CONCLUSION
        # ====================================================

        st.divider()

        st.subheader(
            " The scientific conclusion..."
        )

        st.write(
            "This model has absolutely no scientific credibility.😂"
        )



        # ====================================================
        # PHOTO MEMORIES
        # ====================================================

        st.divider()

        st.title(
            "📸 Few moments of us ❤️"
        )


        supported_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".bmp",
            ".gif"
        )

        photos = []

        if os.path.exists(
            PHOTO_FOLDER
        ):

            photos = sorted(
                filename
                for filename in os.listdir(
                    PHOTO_FOLDER
                )
                if filename.lower().endswith(
                    supported_extensions
                )
            )


        photo_memories = {

            "moment_01.jpg": {
                "title": "First Adventure",
                "text": ""
            },

            "moment_02.jpg": {
                "title": "Random Evening",
                "text": ""
            },

            "moment_03.jpg": {
                "title": "Our Funniest Moment",
                "text": ""
            },

            "moment_04.jpg": {
                "title": "One of My Favorites",
                "text": ""
            },

            "moment_05.jpg": {
                "title": "The Little Things",
                "text": ""
            },

            "moment_06.jpg": {
                "title": "One I Keep Coming Back To",
                "text": ""
            }
        }


        valid_photos = []
        invalid_photos = []


        for photo in photos:

            photo_path = os.path.join(
                PHOTO_FOLDER,
                photo
            )

            try:

                with Image.open(
                    photo_path
                ) as image:

                    image.verify()

                valid_photos.append(
                    photo
                )

            except Exception:

                invalid_photos.append(
                    photo
                )


        if invalid_photos:

            st.warning(
                "I couldn't read these photos: "
                + ", ".join(invalid_photos)
                + ". They were skipped."
            )


        if not valid_photos:

            st.info(
                "📸 Add some photos to the "
                "photos folder to see your "
                "memories here."
            )

        else:

            for i in range(
                0,
                len(valid_photos),
                2
            ):

                col1, col2 = st.columns(2)


                with col1:

                    display_photo(
                        valid_photos[i],
                        photo_memories
                    )


                if (
                    i + 1
                    < len(valid_photos)
                ):

                    with col2:

                        display_photo(
                            valid_photos[i + 1],
                            photo_memories
                        )


        # ====================================================
        # OUR STORY
        # ====================================================

        st.divider()

        st.title(
            "Our Story..."
        )

        st.caption(
            "From the day it started to everything "
            "that came after."
        )


        timeline = [

            {
                "date": "...Today — and Still...",
                "title": "❤️",
                "text": (
                    "Through every high, every low, "
                    "and all the ordinary moments "
                    "choosing you is the Best thing I do."
                )
            }
        ]


        for i, moment in enumerate(
            timeline
        ):

            st.subheader(
                f" {moment['date']}"
            )

            st.markdown(
                f"### {moment['title']}"
            )

            st.write(
                moment["text"]
            )

            if i < len(timeline) - 1:

                st.divider()


        # ====================================================
        # LETTER
        # ====================================================

        st.divider()

        st.title(
            "💌 A Little Something From Me"
        )


        st.subheader(
            "Dear❤️,"
        )

        st.write(
            """
I don't know if I can put everything I feel
into a words, but I wanted to try.

Thank you for all the little moments, the laughs,
the conversations, the random memories, and even
the moments that didn't go exactly as planned.


I'm grateful for every chapter we've already
written, and even more excited about all the ones
still waiting for us.💖
"""
        )



        # ====================================================
        # FINAL BIRTHDAY REVEAL
        # ====================================================

        st.divider()

        st.title(
            "🎂 Happy Birthday 🥳❤️"
        )

        st.subheader(
                    "with soo much love"
                )

        st.success(
            "🤞💫💝"
        )

       