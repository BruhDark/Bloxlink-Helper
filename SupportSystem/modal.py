import discord
from discord.ui import InputText, Modal
import datetime
from config import EMOTES, LINKS, COLORS
from Resources.mongoFunctions import find_one, insert_one, update_one

class FAQCreateModal(Modal):
    def __init__(self, category,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs, title="Create FAQ")
        self.category: str = category

        self.add_item(InputText(label="Question", placeholder="Type the question here", style=discord.InputTextStyle.short))
        self.add_item(InputText(label="Answer", placeholder="Type the answer here", style=discord.InputTextStyle.long))
        self.add_item(InputText(label="Image URL", placeholder="Paste a image URL here", style=discord.InputTextStyle.short, value=None, required=False))

    async def callback(self, interaction: discord.Interaction):
            
            question = self.children[0].value
            answer = self.children[1].value.replace("\\n", "\n")
            image = self.children[2].value

    
            newFAQ = {"q": question, "a": answer}
    
            check = {"q": question}
    
            find = await find_one(f"faq-{self.category}", check)
    
            if find:
                error = EMOTES["error"]
                embed = discord.Embed(
                    description=f"{error} A FAQ with that question already exists!", color=COLORS["error"])
                await interaction.response.send_message(embed=embed)
                return
    
            item = await insert_one(f"faq-{self.category}", newFAQ)
    
            embed = discord.Embed(
                    title=f":paperclips: Question: {question}", description=f":page_with_curl: Answer:\n{answer}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.set_footer(
                    icon_url=LINKS["other"], text=f"Item ID: {item.inserted_id}")
            embed.set_author(
                    icon_url=LINKS["success"], name=f"Successfully created FAQ: {question}")
    
            await interaction.response.send_message(embed=embed)

class FAQEditModal(Modal):
    def __init__(self, category, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, title="Edit FAQ")
        self.category = category

        self.add_item(InputText(label="Question", placeholder="The question you will edit (case sensitive)", style=discord.InputTextStyle.short))
        self.add_item(InputText(label="Answer", placeholder="Type the answer here", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        question = self.children[0].value
        answer = self.children[1].value.replace("\\n", "\n")

        check = {"q": question}

        find = await find_one(f"faq-{self.category}", check)

        if not find:
            error = EMOTES["error"]
            embed = discord.Embed(
                description=f"{error} No FAQ with that ID exists!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed)
            return

        else:
            update = {"a": answer}
            await update_one(f"faq-{self.category}", check, update)

            embed = discord.Embed(
                title=f":paperclips: Question: {find['q']}", description=f":page_with_curl: Answer:\n{answer}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.set_footer(
                icon_url=LINKS["other"], text=f"Item ID: {id}")
            embed.set_author(
                icon_url=LINKS["success"], name=f"Successfully edited FAQ: {find['q']}")

            await interaction.response.send_message(embed=embed)
            return