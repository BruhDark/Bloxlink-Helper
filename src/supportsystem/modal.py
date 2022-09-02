import discord
from discord.ui import InputText, Modal
import datetime
from config import emotes, links, colors
from resources.mongoFunctions import find_one, insert_one, return_all, return_all_tags, update_one


class FAQCreateModal(Modal):
    def __init__(self, category, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, title="Create FAQ")
        self.category: str = category

        self.add_item(InputText(
            label="Question", placeholder="Type the question here", style=discord.InputTextStyle.short))
        self.add_item(InputText(
            label="Answer", placeholder="Type the answer here", style=discord.InputTextStyle.long))
        self.add_item(InputText(label="Image URL", placeholder="Paste a image URL here",
                      style=discord.InputTextStyle.short, value=None, required=False))

    async def callback(self, interaction: discord.Interaction):

        question = self.children[0].value
        answer = self.children[1].value.replace("\\n", "\n")
        image = self.children[2].value

        newFAQ = {"q": question, "a": answer, "image": image}

        check = {"q": question}

        find = await find_one(f"faq-{self.category}", check)

        if find:
            error = emotes.error
            embed = discord.Embed(
                description=f"{error} A FAQ with that question already exists!", color=colors.error)
            await interaction.response.send_message(embed=embed)
            return

        item = await insert_one(f"faq-{self.category}", newFAQ)

        embed = discord.Embed(
            title=f":paperclips: Question: {question}", description=f":page_with_curl: Answer:\n{answer}", color=colors.success, timestamp=datetime.datetime.utcnow())
        embed.set_footer(
            icon_url=links.other, text=f"Item ID: {item.inserted_id}")
        embed.set_author(
            icon_url=links.success, name=f"Successfully created FAQ: {question}")

        if image is not None:
            embed.set_image(url=image)

        await interaction.response.send_message(embed=embed)


class FAQEditModal(Modal):
    def __init__(self, category, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, title="Edit a FAQ question")
        self.category = category

        self.add_item(InputText(
            label="Question ID", placeholder=f"The question number in this category ({self.category})", style=discord.InputTextStyle.short))
        self.add_item(InputText(
            label="Question", placeholder="The new question", style=discord.InputTextStyle.long, required=False, value=None))
        self.add_item(InputText(
            label="Answer", placeholder="The new answer", style=discord.InputTextStyle.long, required=False, value=None))
        self.add_item(InputText(label="Image URL",
                      placeholder="The new image URL", style=discord.InputTextStyle.short, required=False, value=None))

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer()

        questionid = self.children[0].value
        question = self.children[1].value
        answer = self.children[2].value.replace("\\n", "\n")
        image_url = self.children[3].value

        faqs = await return_all(f"faq-{self.category}")
        faqs = [{"index": f"{faqn+1}", "question": f"{faq['q']}"}
                for faqn, faq in enumerate(faqs)]

        get_faq = [faq['question']
                   for faq in faqs if faq['index'] == questionid][0]
        check = {
            "q": get_faq}

        find = await find_one(f"faq-{self.category}", check)

        if not find:
            error = emotes.error
            embed = discord.Embed(
                description=f"{error} No FAQ with that ID exists!", color=colors.error)
            await interaction.followup.send(embed=embed)
            return

        else:

            embed = discord.Embed(
                title=f":paperclips: Question: {question or find['q']}", description=f":page_with_curl: Answer:\n{answer}", color=colors.success, timestamp=datetime.datetime.utcnow())

            update = {}
            if question:
                update["q"] = question
            if answer:
                update["a"] = answer
            if image_url:
                update["image"] = image_url
                embed.set_image(url=image_url)

            await update_one(f"faq-{self.category}", check, update)

            embed.set_author(
                icon_url=links.success, name=f"Successfully edited FAQ number {questionid} from {self.category} category")

            await interaction.followup.send(embed=embed)
            return
