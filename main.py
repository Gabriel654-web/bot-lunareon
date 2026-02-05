# ==============================================================================
# 🌌 LUNAREON BOT — V35 (VERSÃO SEGURA PARA GITHUB/RENDER)
# ==============================================================================

import os
import json
import asyncio
import datetime
import random
import io
import time
import keep_alive  # Importa o sistema para não desligar
from typing import Optional, List

import discord
import nest_asyncio
from discord.ext import commands, tasks
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont, ImageOps

nest_asyncio.apply()

# --- 🔒 SEGURANÇA: O Token agora é pego das configurações do Render ---
TOKEN = os.getenv("DISCORD_TOKEN")

# Cores
COR_PRINCIPAL = 0x5865F2 
COR_SUCESSO = 0x57F287
COR_ERRO = 0xED4245
COR_MONEY = 0xF1C40F 
COR_FUN = 0xFF69B4

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- BANCO DE DADOS ---
def load_db(name):
    if not os.path.exists(name):
        with open(name, 'w') as f: json.dump({}, f)
    try:
        with open(name, 'r') as f: return json.load(f)
    except: return {} 

def save_db(name, data):
    with open(name, 'w') as f: json.dump(data, f, indent=4)

def calcular_bonus_cargos(member: discord.Member):
    shop = load_db("shop.json")
    bonus = 0
    if not shop: return 0
    for item in shop.values():
        if item.get('role_id') and item.get('income_bonus', 0) > 0:
            role = member.guild.get_role(item['role_id'])
            if role and role in member.roles:
                bonus += item.get('income_bonus', 0)
    return bonus

# ==============================================================================
# 🎨 PROCESSAMENTO DE IMAGEM
# ==============================================================================

def criar_mascara_circular(size):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    return mask

async def baixar_avatar(user: discord.Member):
    try:
        data = await user.display_avatar.with_format("png").read()
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        img = img.resize((200, 200))
        mask = criar_mascara_circular(img.size)
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output
    except: return None

async def gerar_imagem_ship(user1, user2, porcentagem):
    bg = Image.new('RGB', (600, 300), (47, 49, 54))
    draw = ImageDraw.Draw(bg)
    av1 = await baixar_avatar(user1)
    av2 = await baixar_avatar(user2)
    if av1: bg.paste(av1, (50, 50), av1)
    if av2: bg.paste(av2, (350, 50), av2)
    draw.rectangle([50, 260, 550, 290], fill=(30, 30, 30))
    largura = 50 + (porcentagem * 5)
    cor = (255, 50, 50) if porcentagem > 60 else (100, 100, 100)
    draw.rectangle([50, 260, largura, 290], fill=cor)
    draw.ellipse([260, 120, 340, 200], fill=(255, 0, 0)) 
    buffer = io.BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

async def gerar_imagem_beijo(user1, user2):
    bg = Image.new('RGB', (600, 300), (255, 182, 193))
    draw = ImageDraw.Draw(bg)
    av1 = await baixar_avatar(user1)
    av2 = await baixar_avatar(user2)
    if av1: bg.paste(av1, (70, 50), av1)
    if av2: bg.paste(av2, (330, 50), av2)
    draw.ellipse([270, 130, 300, 160], fill=(200, 0, 50)) 
    draw.ellipse([300, 130, 330, 160], fill=(200, 0, 50))
    draw.ellipse([280, 150, 320, 180], fill=(200, 0, 50))
    buffer = io.BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# ==============================================================================
# 💖 COMANDOS SOCIAIS
# ==============================================================================

@bot.tree.command(name="ship", description="[Social] Calcular amor")
async def ship(interaction: discord.Interaction, usuario1: discord.Member, usuario2: discord.Member):
    await interaction.response.defer()
    porcentagem = random.randint(0, 100)
    buffer = await gerar_imagem_ship(usuario1, usuario2, porcentagem)
    if buffer:
        file = discord.File(buffer, filename="ship.png")
        embed = discord.Embed(title=f"💘 Ship: {porcentagem}%", color=COR_FUN)
        embed.set_image(url="attachment://ship.png")
        if porcentagem > 80: embed.set_thumbnail(url="https://media1.tenor.com/m/F02Ep3Q2EpJAAAAi/cute-kawai.gif")
        await interaction.followup.send(embed=embed, file=file)
    else: await interaction.followup.send("❌ Erro na imagem.")

@bot.tree.command(name="beijar", description="[Social] Beijar")
async def beijar(interaction: discord.Interaction, usuario: discord.Member):
    await interaction.response.defer()
    buffer = await gerar_imagem_beijo(interaction.user, usuario)
    gifs = ["https://i.pinimg.com/originals/d4/77/6c/d4776c38269d72492976b006dd004a43.gif", "https://i.imgur.com/812893s.gif"]
    if buffer:
        file = discord.File(buffer, filename="beijo.png")
        embed = discord.Embed(description=f"💋 **{interaction.user.mention} beijou {usuario.mention}!**", color=COR_FUN)
        embed.set_image(url="attachment://beijo.png")
        embed.set_thumbnail(url=random.choice(gifs))
        await interaction.followup.send(embed=embed, file=file)
    else: await interaction.followup.send("❌ Erro na imagem.")

@bot.tree.command(name="tapa", description="[Social] Dar tapa")
async def tapa(interaction: discord.Interaction, usuario: discord.Member):
    gifs = ["https://i.imgur.com/4MQkDKm.gif", "https://i.pinimg.com/originals/fe/39/f2/fe39f2d059069d8058a9707e2c94d072.gif", "https://i.imgur.com/o2SJYUS.gif"]
    embed = discord.Embed(description=f"💢 **{interaction.user.mention} deu um tapa em {usuario.mention}!**", color=COR_ERRO)
    embed.set_image(url=random.choice(gifs))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="abraco", description="[Social] Abraçar")
async def abraco(interaction: discord.Interaction, usuario: discord.Member):
    gifs = ["https://i.pinimg.com/originals/85/72/a1/8572a1d1ebaa45fae290e6760b59caac.gif", "https://i.imgur.com/r9aU2xv.gif"]
    embed = discord.Embed(description=f"🤗 **{interaction.user.mention} abraçou {usuario.mention}!**", color=COR_FUN)
    embed.set_image(url=random.choice(gifs))
    await interaction.response.send_message(embed=embed)

# ==============================================================================
# 🚨 WARNS
# ==============================================================================

@bot.tree.command(name="warn", description="[Staff] Dar aviso")
@app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, membro: discord.Member, motivo: str):
    warns = load_db("warns.json")
    uid = str(membro.id)
    if uid not in warns: warns[uid] = []
    warns[uid].append({"motivo": motivo, "staff": interaction.user.name, "data": datetime.datetime.now().strftime("%d/%m")})
    save_db("warns.json", warns)
    await interaction.response.send_message(embed=discord.Embed(title="⚠️ Warn", description=f"Em: {membro.mention}\nMotivo: {motivo}", color=COR_ERRO))

@bot.tree.command(name="historico", description="[Staff] Ver Warns")
async def historico(interaction: discord.Interaction, membro: discord.Member):
    warns = load_db("warns.json").get(str(membro.id), [])
    if not warns: return await interaction.response.send_message("✅ Limpo.", ephemeral=True)
    embed = discord.Embed(title=f"📂 Warns: {membro.name}", color=COR_PRINCIPAL)
    txt = ""
    for i, w in enumerate(warns[-15:], 1): txt += f"**{i}.** {w['motivo']} ({w['data']})\n"
    embed.description = txt
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unwarn", description="[Staff] Remover Warn")
@app_commands.checks.has_permissions(kick_members=True)
async def unwarn(interaction: discord.Interaction, membro: discord.Member, numero: int):
    warns = load_db("warns.json")
    uid = str(membro.id)
    if uid in warns and 1 <= numero <= len(warns[uid]):
        warns[uid].pop(numero-1)
        save_db("warns.json", warns)
        await interaction.response.send_message("✅ Removido.")
    else: await interaction.response.send_message("❌ Inválido.", ephemeral=True)

# ==============================================================================
# 🎁 SISTEMA DE SORTEIO (GIVEAWAY)
# ==============================================================================

class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Participar", style=discord.ButtonStyle.primary, emoji="🎉", custom_id="gw_join_btn")
    async def join_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        gw_db = load_db("giveaways.json")
        msg_id = str(interaction.message.id)

        if msg_id not in gw_db:
            return await interaction.response.send_message("❌ Este sorteio já acabou ou não existe.", ephemeral=True)

        gw_data = gw_db[msg_id]
        
        # Verificar Cargo Opcional
        if gw_data.get("role_req"):
            role = interaction.guild.get_role(gw_data["role_req"])
            if role and role not in interaction.user.roles:
                return await interaction.response.send_message(f"🔒 Você precisa do cargo **{role.name}** para participar!", ephemeral=True)

        # Adicionar participante
        if interaction.user.id in gw_data["entries"]:
            gw_data["entries"].remove(interaction.user.id)
            save_db("giveaways.json", gw_db)
            await interaction.response.send_message("📤 Você saiu do sorteio.", ephemeral=True)
        else:
            gw_data["entries"].append(interaction.user.id)
            save_db("giveaways.json", gw_db)
            await interaction.response.send_message("✅ Você entrou no sorteio!", ephemeral=True)
        
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Participantes: {len(gw_data['entries'])} | Termina em breve")
        await interaction.message.edit(embed=embed)

@bot.tree.command(name="sorteio", description="[Admin] Criar um sorteio")
@app_commands.checks.has_permissions(manage_guild=True)
async def create_giveaway(interaction: discord.Interaction, premio: str, minutos: int, descricao: str, cargo_requisito: discord.Role = None):
    end_time = datetime.datetime.now().timestamp() + (minutos * 60)
    embed = discord.Embed(title="🎉 NOVO SORTEIO! 🎉", description=f"**Prêmio:** {premio}\n\n📝 **Descrição:** {descricao}\n\n⏳ **Duração:** {minutos} minutos", color=COR_FUN)
    if cargo_requisito:
        embed.add_field(name="🔒 Requisito", value=f"Necessário cargo {cargo_requisito.mention}", inline=False)
    embed.set_footer(text="Participantes: 0 | Clique no botão abaixo!")
    embed.set_thumbnail(url="https://media.tenor.com/J3iY6N1jT7AAAAAi/party-popper-joypixels.gif")

    await interaction.response.send_message(embed=embed, view=GiveawayView())
    msg = await interaction.original_response()

    gw_db = load_db("giveaways.json")
    gw_db[str(msg.id)] = {
        "channel_id": interaction.channel_id,
        "premio": premio,
        "end_time": end_time,
        "role_req": cargo_requisito.id if cargo_requisito else None,
        "entries": []
    }
    save_db("giveaways.json", gw_db)

@tasks.loop(seconds=30)
async def check_giveaways():
    gw_db = load_db("giveaways.json")
    now = datetime.datetime.now().timestamp()
    to_remove = []

    for msg_id, data in gw_db.items():
        if now >= data["end_time"]:
            channel = bot.get_channel(data["channel_id"])
            if channel:
                try:
                    msg = await channel.fetch_message(int(msg_id))
                    entries = data["entries"]
                    if not entries:
                        winner_text = "Ninguém participou 😢"
                    else:
                        winner_id = random.choice(entries)
                        winner_text = f"<@{winner_id}>"
                        await channel.send(f"🎉 **PARABÉNS** {winner_text}! Você ganhou: **{data['premio']}**! 🎁")
                    embed = msg.embeds[0]
                    embed.title = "🎊 SORTEIO ENCERRADO 🎊"
                    embed.color = 0x2F3136
                    embed.clear_fields()
                    embed.add_field(name="🏆 Ganhador", value=winner_text)
                    embed.add_field(name="🎁 Prêmio", value=data['premio'])
                    embed.set_footer(text="Sorteio finalizado.")
                    await msg.edit(embed=embed, view=None)
                except: pass
            to_remove.append(msg_id)
    
    if to_remove:
        for mid in to_remove:
            del gw_db[mid]
        save_db("giveaways.json", gw_db)

# ==============================================================================
# 💸 ECONOMIA, LOJA E INVENTÁRIO
# ==============================================================================

class ShopSelect(discord.ui.Select):
    def __init__(self, shop_items):
        options = []
        if shop_items:
            for k, v in list(shop_items.items())[:25]:
                if v: 
                    label = f"{v.get('nome','Item')}"
                    desc = f"R$ {v.get('valor',0)} | {v.get('descricao', 'Sem descrição')[:30]}"
                    options.append(discord.SelectOption(label=label, description=desc, emoji=v.get('emoji','📦'), value=k))
        if not options: options.append(discord.SelectOption(label="Vazio", value="empty"))
        super().__init__(placeholder="🛒 Selecione para comprar...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "empty": return await interaction.response.send_message("❌ Vazio.", ephemeral=True)
        item = load_db("shop.json").get(self.values[0])
        eco, inv, uid = load_db("economy.json"), load_db("inventory.json"), str(interaction.user.id)
        
        if eco.get(uid, 0) < item['valor']: 
            return await interaction.response.send_message(f"❌ Você precisa de R$ {item['valor']}.", ephemeral=True)
        
        eco[uid] -= item['valor']
        if uid not in inv: inv[uid] = {}
        if isinstance(inv[uid], list): inv[uid] = {} 
        item_key = item['nome']
        inv[uid][item_key] = inv[uid].get(item_key, 0) + 1
        
        msg_extra = ""
        if item.get('role_id'):
            r = interaction.guild.get_role(item['role_id'])
            if r: 
                await interaction.user.add_roles(r)
                msg_extra = f"\n🔥 **Cargo {r.mention} adicionado ao seu perfil!**"
            
        save_db("economy.json", eco)
        save_db("inventory.json", inv)
        
        embed = discord.Embed(title="✅ Compra Realizada", description=f"Você comprou **{item['nome']}** por R$ {item['valor']}.{msg_extra}", color=COR_SUCESSO)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="loja", description="[Eco] Abrir Loja Visual")
async def loja(interaction: discord.Interaction):
    shop = load_db("shop.json")
    if not shop: return await interaction.response.send_message("❌ Loja fechada.", ephemeral=True)
    embed = discord.Embed(title="🛒 Loja do Servidor", description="Compre itens e receba cargos automaticamente!", color=COR_MONEY)
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    for v in shop.values():
        bonus_txt = f" | 📈 +R${v.get('income_bonus',0)}/dia" if v.get('income_bonus',0) > 0 else ""
        desc = v.get('descricao', 'Item da loja')
        embed.add_field(name=f"{v.get('emoji','📦')} {v['nome']}", value=f"```\n💳 Preço: R$ {v['valor']}\n📝 {desc}{bonus_txt}\n```", inline=False)
    embed.set_footer(text="Ao comprar, você recebe o item e o cargo na hora!")
    await interaction.response.send_message(embed=embed, view=discord.ui.View().add_item(ShopSelect(shop)))

@bot.tree.command(name="inventario", description="[Eco] Ver seus itens")
async def inventario(interaction: discord.Interaction):
    inv = load_db("inventory.json").get(str(interaction.user.id), {})
    if isinstance(inv, list): inv = {} 
    if not inv: return await interaction.response.send_message("🎒 Mochila vazia.", ephemeral=True)
    embed = discord.Embed(title=f"🎒 Mochila de {interaction.user.name}", color=COR_PRINCIPAL)
    txt = ""
    for nome, qtd in inv.items():
        if qtd > 0: txt += f"**{qtd}x** {nome}\n"
    embed.description = txt if txt else "Nada aqui."
    embed.set_footer(text="Use /usar [nome] para consumir o item.")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="usar", description="[Eco] Consumir item do inventário")
async def usar(interaction: discord.Interaction, nome_item: str):
    uid = str(interaction.user.id)
    inv = load_db("inventory.json")
    user_inv = inv.get(uid, {})
    item_real_name = None
    for k in user_inv.keys():
        if k.lower() == nome_item.lower():
            item_real_name = k
            break
    if not item_real_name or user_inv[item_real_name] <= 0:
        return await interaction.response.send_message("❌ Você não tem este item.", ephemeral=True)
    inv[uid][item_real_name] -= 1
    if inv[uid][item_real_name] <= 0:
        del inv[uid][item_real_name]
    save_db("inventory.json", inv)
    await interaction.response.send_message(f"✨ Você usou/consumiu **{item_real_name}**.", ephemeral=True)

@bot.tree.command(name="admin_dar_item", description="[Admin] Dar item")
@app_commands.checks.has_permissions(administrator=True)
async def admin_dar_item(interaction: discord.Interaction, membro: discord.Member, nome_item: str, quantidade: int = 1):
    uid = str(membro.id)
    inv = load_db("inventory.json")
    if uid not in inv: inv[uid] = {}
    target_key = nome_item
    for k in inv[uid]:
        if k.lower() == nome_item.lower():
            target_key = k
            break
    inv[uid][target_key] = inv[uid].get(target_key, 0) + quantidade
    save_db("inventory.json", inv)
    await interaction.response.send_message(f"🎁 Você deu **{quantidade}x {nome_item}** para {membro.mention}.")

@bot.tree.command(name="admin_tira_item", description="[Admin] Tirar item")
@app_commands.checks.has_permissions(administrator=True)
async def admin_tira_item(interaction: discord.Interaction, membro: discord.Member, nome_item: str, quantidade: int = 1):
    uid = str(membro.id)
    inv = load_db("inventory.json")
    item_key = None
    if uid in inv:
        for k in inv[uid].keys():
            if k.lower() == nome_item.lower():
                item_key = k
                break
    if not item_key: return await interaction.response.send_message(f"❌ {membro.name} não tem o item **{nome_item}**.", ephemeral=True)
    inv[uid][item_key] -= quantidade
    if inv[uid][item_key] <= 0: del inv[uid][item_key]
    save_db("inventory.json", inv)
    await interaction.response.send_message(f"🗑️ Removido **{quantidade}x {item_key}** de {membro.name}.")

@bot.tree.command(name="admin_loja_add", description="[Admin] Criar Item na Loja")
@app_commands.checks.has_permissions(administrator=True)
async def loja_add(interaction: discord.Interaction, nome: str, valor: int, emoji: str, descricao: str = "Item incrível", cargo: discord.Role = None, bonus: int = 0):
    shop = load_db("shop.json")
    shop[nome.lower().replace(" ", "_")] = {
        "nome": nome, "valor": valor, "emoji": emoji, 
        "descricao": descricao,
        "role_id": cargo.id if cargo else None, "income_bonus": bonus
    }
    save_db("shop.json", shop)
    await interaction.response.send_message("✅ Item adicionado à loja com sucesso!")

@bot.tree.command(name="admin_loja_remove", description="[Admin] Remover Item da Loja")
@app_commands.checks.has_permissions(administrator=True)
async def loja_remove(interaction: discord.Interaction, nome_item: str):
    shop = load_d
