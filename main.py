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
    shop = load_db("shop.json")
    iid = nome_item.lower().replace(" ", "_")
    if iid in shop:
        del shop[iid]
        save_db("shop.json", shop)
        await interaction.response.send_message("✅ Item removido da loja.")
    else: await interaction.response.send_message("❌ Não encontrado.")

@bot.tree.command(name="admin_loja_reset", description="[Admin] Resetar Loja")
@app_commands.checks.has_permissions(administrator=True)
async def loja_reset(interaction: discord.Interaction):
    save_db("shop.json", {})
    await interaction.response.send_message("✅ Loja resetada.")

@bot.tree.command(name="cassino", description="[Eco] Apostar")
async def cassino(interaction: discord.Interaction, valor: int):
    eco = load_db("economy.json")
    uid = str(interaction.user.id)
    saldo = eco.get(uid, 0)
    if valor <= 0 or saldo < valor: return await interaction.response.send_message("❌ Valor inválido.", ephemeral=True)
    if random.random() < 0.40:
        eco[uid] += valor 
        embed = discord.Embed(title="🎰 GANHOU!", description=f"Lucro: +R$ {valor}\nSaldo: R$ {eco[uid]}", color=COR_SUCESSO)
    else:
        eco[uid] -= valor
        embed = discord.Embed(title="🎰 PERDEU!", description=f"Prejuízo: -R$ {valor}\nSaldo: R$ {eco[uid]}", color=COR_ERRO)
    save_db("economy.json", eco)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="salario", description="[Eco] Diária")
async def salario(interaction: discord.Interaction):
    cd, uid = load_db("cooldowns.json"), str(interaction.user.id)
    if uid in cd and "daily" in cd[uid] and time.time() - cd[uid]["daily"] < 86400: return await interaction.response.send_message("⏳ Volte amanhã.", ephemeral=True)
    val = 1000 + calcular_bonus_cargos(interaction.user)
    eco = load_db("economy.json")
    eco[uid] = eco.get(uid, 0) + val
    if uid not in cd: cd[uid] = {}
    cd[uid]["daily"] = time.time()
    save_db("economy.json", eco); save_db("cooldowns.json", cd)
    await interaction.response.send_message(f"💰 Recebeu **R$ {val}**")

@bot.tree.command(name="trabalhar", description="[Eco] Trabalhar")
async def trabalhar(interaction: discord.Interaction):
    cd, uid = load_db("cooldowns.json"), str(interaction.user.id)
    if uid in cd and "work" in cd[uid] and time.time() - cd[uid]["work"] < 3600: return await interaction.response.send_message("⏳ Espere 1h.", ephemeral=True)
    val = random.randint(100, 500) + calcular_bonus_cargos(interaction.user)
    eco = load_db("economy.json")
    eco[uid] = eco.get(uid, 0) + val
    if uid not in cd: cd[uid] = {}
    cd[uid]["work"] = time.time()
    save_db("economy.json", eco); save_db("cooldowns.json", cd)
    await interaction.response.send_message(f"⚒️ Ganhou **R$ {val}**")

@bot.tree.command(name="atm", description="[Eco] Saldo")
async def atm(interaction: discord.Interaction, usuario: discord.Member = None):
    u = usuario or interaction.user
    await interaction.response.send_message(f"💳 **{u.name}**: R$ {load_db('economy.json').get(str(u.id), 0)}")

@bot.tree.command(name="transferir", description="[Eco] Pagar")
async def transferir(interaction: discord.Interaction, membro: discord.Member, valor: int):
    eco = load_db("economy.json")
    uid, tid = str(interaction.user.id), str(membro.id)
    if eco.get(uid, 0) < valor or valor <= 0: return await interaction.response.send_message("❌ Inválido.", ephemeral=True)
    eco[uid] -= valor
    eco[tid] = eco.get(tid, 0) + valor
    save_db("economy.json", eco)
    await interaction.response.send_message(f"💸 Pago **R$ {valor}** para {membro.name}.")

@bot.tree.command(name="rank", description="[Eco] Top Ricos")
async def rank(interaction: discord.Interaction):
    eco = load_db("economy.json")
    ranking = sorted(eco.items(), key=lambda x: x[1], reverse=True)[:10]
    txt = "\n".join([f"{i+1}. <@{uid}> - R$ {s}" for i, (uid, s) in enumerate(ranking)])
    await interaction.response.send_message(embed=discord.Embed(title="🏆 Rank", description=txt or "Vazio", color=COR_MONEY))

@bot.tree.command(name="admin_add_money", description="[Admin] Dar dinheiro")
@app_commands.checks.has_permissions(administrator=True)
async def add_money(interaction: discord.Interaction, membro: discord.Member, valor: int):
    eco = load_db("economy.json")
    eco[str(membro.id)] = eco.get(str(membro.id), 0) + valor
    save_db("economy.json", eco)
    await interaction.response.send_message(f"✅ Adicionado R$ {valor}.")

@bot.tree.command(name="admin_remove_money", description="[Admin] Tirar dinheiro")
@app_commands.checks.has_permissions(administrator=True)
async def remove_money(interaction: discord.Interaction, membro: discord.Member, valor: int):
    eco = load_db("economy.json")
    eco[str(membro.id)] = max(0, eco.get(str(membro.id), 0) - valor)
    save_db("economy.json", eco)
    await interaction.response.send_message(f"💸 Removido R$ {valor}.")

# ==============================================================================
# 🛠️ MODERAÇÃO & TICKETS
# ==============================================================================

@bot.tree.command(name="ban", description="[Mod] Banir")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
    await interaction.guild.ban(membro, reason=motivo)
    await interaction.response.send_message(f"🔨 {membro.name} banido.")

@bot.tree.command(name="kick", description="[Mod] Expulsar")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
    await interaction.guild.kick(membro, reason=motivo)
    await interaction.response.send_message(f"👢 {membro.name} expulso.")

@bot.tree.command(name="lock", description="[Mod] Trancar canal")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Canal trancado.")

@bot.tree.command(name="unlock", description="[Mod] Destrancar canal")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Canal destrancado.")

@bot.tree.command(name="limpar", description="[Mod] Limpar chat")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar(interaction: discord.Interaction, quantidade: int):
    await interaction.response.defer(ephemeral=True) 
    d = await interaction.channel.purge(limit=min(quantidade, 100))
    await interaction.followup.send(f"🧹 {len(d)} deletadas.", ephemeral=True)

@bot.tree.command(name="say", description="[Admin] Falar")
@app_commands.checks.has_permissions(administrator=True)
async def say(interaction: discord.Interaction, mensagem: str):
    await interaction.channel.send(mensagem)
    await interaction.response.send_message("✅", ephemeral=True)

@bot.tree.command(name="avatar", description="[Util] Ver foto")
async def avatar(interaction: discord.Interaction, membro: discord.Member = None):
    u = membro or interaction.user
    await interaction.response.send_message(embed=discord.Embed(color=COR_FUN).set_image(url=u.display_avatar.url))

@bot.tree.command(name="serverinfo", description="[Util] Info do server")
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=f"Info: {g.name}", color=COR_PRINCIPAL)
    if g.icon: embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="Dono", value=g.owner.mention)
    embed.add_field(name="Membros", value=str(g.member_count))
    await interaction.response.send_message(embed=embed)

class TicketControl(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Assumir", style=discord.ButtonStyle.success, emoji="🙋‍♂️", custom_id="tk_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.edit(topic=f"Atendente: {interaction.user.name}")
        await interaction.response.send_message(f"✅ {interaction.user.mention} assumiu.")
    @discord.ui.button(label="Fechar", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="tk_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Fechando...")
        await asyncio.sleep(2)
        await interaction.channel.delete()

class MultiTicketLauncher(discord.ui.View):
    def __init__(self, configs=None):
        super().__init__(timeout=None)
        if configs:
            for c in configs: self.add_item(discord.ui.Button(label=c['label'], style=discord.ButtonStyle.blurple, emoji="📩", custom_id=f"tk_open_{c['role_id']}"))
    async def interaction_check(self, interaction: discord.Interaction):
        if "tk_open" in interaction.data['custom_id']:
            rid = int(interaction.data['custom_id'].split("_")[-1])
            role = interaction.guild.get_role(rid)
            cname = f"ticket-{interaction.user.name.lower()[:5]}"
            if discord.utils.get(interaction.guild.channels, name=cname): return await interaction.response.send_message("❌ Já tem ticket.", ephemeral=True)
            overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True), interaction.guild.me: discord.PermissionOverwrite(read_messages=True)}
            if role: overwrites[role] = discord.PermissionOverwrite(read_messages=True)
            c = await interaction.guild.create_text_channel(cname, overwrites=overwrites)
            await c.send(f"{interaction.user.mention}", embed=discord.Embed(title="Suporte", description="Aguarde.", color=COR_PRINCIPAL), view=TicketControl())
            await interaction.response.send_message(f"✅ {c.mention}", ephemeral=True)
        return False

@bot.tree.command(name="setup_ticket", description="[Admin] Painel Tickets")
@app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction, titulo: str, b1_nome: str, b1_cargo: discord.Role, b2_nome: str = None, b2_cargo: discord.Role = None, b3_nome: str = None, b3_cargo: discord.Role = None):
    configs = [{'label': b1_nome, 'role_id': b1_cargo.id}]
    if b2_nome and b2_cargo: configs.append({'label': b2_nome, 'role_id': b2_cargo.id})
    if b3_nome and b3_cargo: configs.append({'label': b3_nome, 'role_id': b3_cargo.id})
    await interaction.channel.send(embed=discord.Embed(title=titulo, color=COR_PRINCIPAL), view=MultiTicketLauncher(configs))
    await interaction.response.send_message("✅ Painel criado.", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(TicketControl())
    bot.add_view(GiveawayView())
    if not check_giveaways.is_running():
        check_giveaways.start()
    await bot.tree.sync()
    print(f"🚀 {bot.user} ONLINE (V35)")

# ATIVA O KEEP_ALIVE ANTES DE LIGAR
keep_alive.keep_alive()
bot.run(TOKEN)