# ==============================================================================
# 🌌 LUNAREON BOT — V35 (VERSÃO FINAL SEM ERROS)
# ==============================================================================

import os
import json
import asyncio
import datetime
import random
import io
from typing import Optional

import discord
from discord.ext import commands, tasks
from discord import app_commands
from PIL import Image, ImageDraw, ImageOps

# --- 🌐 SERVIDOR WEB (PARA MANTER O BOT ONLINE NO RENDER) ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Lunareon Bot está Online! 🚀"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ⚙️ CONFIGURAÇÕES ---
TOKEN = os.getenv("DISCORD_TOKEN")  # Pega o token das variaveis de ambiente

# Cores do Embed
COR_PRINCIPAL = 0x5865F2 
COR_SUCESSO = 0x57F287
COR_ERRO = 0xED4245
COR_MONEY = 0xF1C40F 
COR_FUN = 0xFF69B4

# Configuração do Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- 💾 SISTEMA DE BANCO DE DADOS (JSON) ---
def load_db(name):
    if not os.path.exists(name):
        with open(name, 'w') as f: json.dump({}, f)
    try:
        with open(name, 'r') as f: return json.load(f)
    except: return {} 

def save_db(name, data):
    with open(name, 'w') as f: json.dump(data, f, indent=4)

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
        # Tenta baixar o avatar. Se falhar, retorna None
        if not user.display_avatar: return None
        data = await user.display_avatar.with_format("png").read()
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        img = img.resize((200, 200))
        mask = criar_mascara_circular(img.size)
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output
    except Exception as e:
        print(f"Erro ao baixar avatar: {e}")
        return None

async def gerar_imagem_ship(user1, user2, porcentagem):
    bg = Image.new('RGB', (600, 300), (47, 49, 54))
    draw = ImageDraw.Draw(bg)
    
    av1 = await baixar_avatar(user1)
    av2 = await baixar_avatar(user2)
    
    if av1: bg.paste(av1, (50, 50), av1)
    if av2: bg.paste(av2, (350, 50), av2)
    
    # Barra de progresso
    draw.rectangle([50, 260, 550, 290], fill=(30, 30, 30))
    largura = 50 + (porcentagem * 5)
    cor = (255, 50, 50) if porcentagem > 60 else (100, 100, 100)
    draw.rectangle([50, 260, largura, 290], fill=cor)
    
    # Coração
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
    
    # Efeitos de beijo
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

@bot.tree.command(name="ship", description="[Social] Calcular amor entre duas pessoas")
async def ship(interaction: discord.Interaction, usuario1: discord.Member, usuario2: discord.Member):
    await interaction.response.defer() # Evita erro de timeout
    porcentagem = random.randint(0, 100)
    try:
        buffer = await gerar_imagem_ship(usuario1, usuario2, porcentagem)
        file = discord.File(buffer, filename="ship.png")
        embed = discord.Embed(title=f"💘 Ship: {porcentagem}%", color=COR_FUN)
        embed.set_image(url="attachment://ship.png")
        
        msg_extra = "São feitos um para o outro!" if porcentagem > 80 else "Talvez precisem de terapia..."
        embed.set_footer(text=msg_extra)
        
        await interaction.followup.send(embed=embed, file=file)
    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao gerar imagem: {e}")

@bot.tree.command(name="beijar", description="[Social] Dar um beijo em alguém")
async def beijar(interaction: discord.Interaction, usuario: discord.Member):
    await interaction.response.defer()
    try:
        buffer = await gerar_imagem_beijo(interaction.user, usuario)
        gifs = ["https://i.pinimg.com/originals/d4/77/6c/d4776c38269d72492976b006dd004a43.gif", "https://media.tenor.com/F02Ep3Q2EpJAAAAi/cute-kawai.gif"]
        
        file = discord.File(buffer, filename="beijo.png")
        embed = discord.Embed(description=f"💋 **{interaction.user.mention} beijou {usuario.mention}!**", color=COR_FUN)
        embed.set_image(url="attachment://beijo.png")
        embed.set_thumbnail(url=random.choice(gifs))
        
        await interaction.followup.send(embed=embed, file=file)
    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao gerar imagem: {e}")

# ==============================================================================
# 🚨 SISTEMA DE WARNS
# ==============================================================================

@bot.tree.command(name="warn", description="[Staff] Dar um aviso para um membro")
@app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, membro: discord.Member, motivo: str):
    warns = load_db("warns.json")
    uid = str(membro.id)
    if uid not in warns: warns[uid] = []
    
    warns[uid].append({"motivo": motivo, "staff": interaction.user.name, "data": datetime.datetime.now().strftime("%d/%m")})
    save_db("warns.json", warns)
    
    await interaction.response.send_message(embed=discord.Embed(title="⚠️ Warn Aplicado", description=f"👤 **Membro:** {membro.mention}\n📄 **Motivo:** {motivo}", color=COR_ERRO))

@bot.tree.command(name="historico", description="[Staff] Ver histórico de avisos")
async def historico(interaction: discord.Interaction, membro: discord.Member):
    warns = load_db("warns.json").get(str(membro.id), [])
    if not warns: return await interaction.response.send_message("✅ Este usuário está limpo.", ephemeral=True)
    
    embed = discord.Embed(title=f"📂 Histórico: {membro.name}", color=COR_PRINCIPAL)
    txt = ""
    for i, w in enumerate(warns[-10:], 1): 
        txt += f"**{i}.** {w['motivo']} (Por: {w['staff']} em {w['data']})\n"
    embed.description = txt
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unwarn", description="[Staff] Remover um aviso")
@app_commands.checks.has_permissions(kick_members=True)
async def unwarn(interaction: discord.Interaction, membro: discord.Member, numero: int):
    warns = load_db("warns.json")
    uid = str(membro.id)
    
    if uid in warns and 1 <= numero <= len(warns[uid]):
        removido = warns[uid].pop(numero-1)
        save_db("warns.json", warns)
        await interaction.response.send_message(f"✅ Warn removido: **{removido['motivo']}**")
    else:
        await interaction.response.send_message("❌ Número de warn inválido.", ephemeral=True)

# ==============================================================================
# 🎁 SISTEMA DE SORTEIO (GIVEAWAY)
# ==============================================================================

class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Timeout None para o botão durar para sempre

    @discord.ui.button(label="Participar", style=discord.ButtonStyle.primary, emoji="🎉", custom_id="gw_join_btn")
    async def join_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        gw_db = load_db("giveaways.json")
        msg_id = str(interaction.message.id)

        if msg_id not in gw_db:
            return await interaction.response.send_message("❌ Este sorteio já acabou ou foi deletado.", ephemeral=True)

        gw_data = gw_db[msg_id]
        
        # Cargo Requisito
        if gw_data.get("role_req"):
            role = interaction.guild.get_role(gw_data["role_req"])
            if role and role not in interaction.user.roles:
                return await interaction.response.send_message(f"🔒 Necessário cargo **{role.name}** para entrar!", ephemeral=True)

        # Entrar/Sair
        uid = interaction.user.id
        if uid in gw_data["entries"]:
            gw_data["entries"].remove(uid)
            save_db("giveaways.json", gw_db)
            await interaction.response.send_message("📤 Você saiu do sorteio.", ephemeral=True)
        else:
            gw_data["entries"].append(uid)
            save_db("giveaways.json", gw_db)
            await interaction.response.send_message("✅ Você está participando!", ephemeral=True)
        
        # Atualiza contador no embed
        try:
            embed = interaction.message.embeds[0]
            embed.set_footer(text=f"Participantes: {len(gw_data['entries'])} | Boa sorte!")
            await interaction.message.edit(embed=embed)
        except: pass

@bot.tree.command(name="sorteio", description="[Admin] Iniciar um sorteio")
@app_commands.checks.has_permissions(manage_guild=True)
async def create_giveaway(interaction: discord.Interaction, premio: str, minutos: int, descricao: str, cargo_requisito: discord.Role = None):
    end_time = datetime.datetime.now().timestamp() + (minutos * 60)
    
    embed = discord.Embed(title="🎉 NOVO SORTEIO! 🎉", description=f"**Prêmio:** {premio}\n\n📝 **Sobre:** {descricao}\n\n⏳ **Duração:** {minutos} minutos", color=COR_FUN)
    if cargo_requisito:
        embed.add_field(name="🔒 Requisito", value=f"Cargo {cargo_requisito.mention}", inline=False)
    embed.set_footer(text="Participantes: 0 | Clique no botão para entrar!")
    
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
                    embed.set_footer(text="Finalizado.")
                    await msg.edit(embed=embed, view=None)
                except Exception as e:
                    print(f"Erro ao finalizar sorteio: {e}")
            to_remove.append(msg_id)
    
    if to_remove:
        for mid in to_remove:
            del gw_db[mid]
        save_db("giveaways.json", gw_db)

# ==============================================================================
# 💸 LOJA E ECONOMIA
# ==============================================================================

class ShopSelect(discord.ui.Select):
    def __init__(self, shop_items):
        options = []
        if shop_items:
            # Discord limita a 25 opções, então pegamos as primeiras 25
            for k, v in list(shop_items.items())[:25]:
                label = f"{v.get('nome','Item')}"
                desc = f"R$ {v.get('valor',0)} | {v.get('descricao', 'Sem descrição')[:30]}"
                emoji = v.get('emoji', '📦')
                options.append(discord.SelectOption(label=label, description=desc, emoji=emoji, value=k))
        
        if not options: 
            options.append(discord.SelectOption(label="Vazio", value="empty"))
        
        super().__init__(placeholder="🛒 Escolha um item para comprar...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "empty": 
            return await interaction.response.send_message("❌ Loja vazia.", ephemeral=True)
            
        item = load_db("shop.json").get(self.values[0])
        eco = load_db("economy.json")
        inv = load_db("inventory.json")
        uid = str(interaction.user.id)
        
        saldo = eco.get(uid, 0)
        
        # Verifica dinheiro
        if saldo < item['valor']: 
            return await interaction.response.send_message(f"❌ Você precisa de R$ {item['valor']} (Saldo: R$ {saldo}).", ephemeral=True)
        
        # Processa compra
        eco[uid] -= item['valor']
        
        if uid not in inv: inv[uid] = {}
        if isinstance(inv[uid], list): inv[uid] = {} # Correção de bug antigo se existir
        
        item_key = item['nome']
        inv[uid][item_key] = inv[uid].get(item_key, 0) + 1
        
        msg_extra = ""
        # Entregar Cargo se tiver
        if item.get('role_id'):
            role = interaction.guild.get_role(item['role_id'])
            if role: 
                try:
                    await interaction.user.add_roles(role)
                    msg_extra = f"\n🔥 **Cargo {role.mention} entregue!**"
                except:
                    msg_extra = "\n⚠️ Não consegui entregar o cargo (sem permissão)."

        save_db("economy.json", eco)
        save_db("inventory.json", inv)
        
        embed = discord.Embed(title="✅ Compra Realizada!", description=f"Você comprou **{item['nome']}** por R$ {item['valor']}.{msg_extra}", color=COR_SUCESSO)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="loja", description="[Eco] Ver itens da loja")
async def loja(interaction: discord.Interaction):
    shop = load_db("shop.json")
    if not shop: 
        return await interaction.response.send_message("❌ A loja está fechada (sem itens).", ephemeral=True)
        
    embed = discord.Embed(title="🛒 Loja do Servidor", description="Use o menu abaixo para comprar.", color=COR_MONEY)
    
    for v in list(shop.values())[:10]: # Mostra os top 10 na descrição
        embed.add_field(name=f"{v.get('emoji','📦')} {v['nome']}", value=f"💰 R$ {v['valor']}\n📝 {v.get('descricao', 'Sem desc.')}", inline=True)
    
    view = discord.ui.View()
    view.add_item(ShopSelect(shop))
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="inventario", description="[Eco] Ver seus itens")
async def inventario(interaction: discord.Interaction):
    inv = load_db("inventory.json").get(str(interaction.user.id), {})
    if isinstance(inv, list): inv = {} # Garante formato dict
    
    embed = discord.Embed(title=f"🎒 Mochila de {interaction.user.name}", color=COR_PRINCIPAL)
    txt = ""
    for nome, qtd in inv.items():
        if qtd > 0: txt += f"• **{qtd}x** {nome}\n"
    
    embed.description = txt if txt else "Nada aqui. Use `/loja` para comprar."
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_loja_add", description="[Admin] Adicionar item à loja")
@app_commands.checks.has_permissions(administrator=True)
async def loja_add(interaction: discord.Interaction, nome: str, valor: int, emoji: str, descricao: str, cargo: discord.Role = None):
    shop = load_db("shop.json")
    # Cria uma chave única baseada no nome
    key = nome.lower().strip().replace(" ", "_")
    
    shop[key] = {
        "nome": nome,
        "valor": valor,
        "emoji": emoji,
        "descricao": descricao,
        "role_id": cargo.id if cargo else None
    }
    save_db("shop.json", shop)
    await interaction.response.send_message(f"✅ Item **{nome}** adicionado à loja por R$ {valor}!")

@bot.tree.command(name="admin_loja_remove", description="[Admin] Remover item da loja")
@app_commands.checks.has_permissions(administrator=True)
async def loja_remove(interaction: discord.Interaction, nome_item: str):
    shop = load_db("shop.json")
    key_to_remove = None
    
    # Procura o item pelo nome ou pela chave
    for k, v in shop.items():
        if k == nome_item or v['nome'].lower() == nome_item.lower():
            key_to_remove = k
            break
            
    if key_to_remove:
        del shop[key_to_remove]
        save_db("shop.json", shop)
        await interaction.response.send_message(f"🗑️ Item **{nome_item}** removido da loja.")
    else:
        await interaction.response.send_message(f"❌ Item **{nome_item}** não encontrado.", ephemeral=True)

@bot.tree.command(name="daily", description="[Eco] Pegar recompensa diária")
async def daily(interaction: discord.Interaction):
    eco = load_db("economy.json")
    uid = str(interaction.user.id)
    
    # Simples sistema de daily sem verificação de tempo para teste (para adicionar tempo, precisa salvar timestamp)
    recompensa = random.randint(100, 500)
    eco[uid] = eco.get(uid, 0) + recompensa
    
    save_db("economy.json", eco)
    await interaction.response.send_message(f"💰 Você recebeu **R$ {recompensa}** hoje! Volte amanhã.")

@bot.tree.command(name="saldo", description="[Eco] Ver seu dinheiro")
async def saldo(interaction: discord.Interaction):
    eco = load_db("economy.json")
    val = eco.get(str(interaction.user.id), 0)
    await interaction.response.send_message(f"💳 Seu saldo: **R$ {val}**")

@bot.tree.command(name="admin_add_money", description="[Admin] Adicionar dinheiro a alguém")
@app_commands.checks.has_permissions(administrator=True)
async def add_money(interaction: discord.Interaction, membro: discord.Member, valor: int):
    eco = load_db("economy.json")
    uid = str(membro.id)
    eco[uid] = eco.get(uid, 0) + valor
    save_db("economy.json", eco)
    await interaction.response.send_message(f"✅ Adicionado **R$ {valor}** para {membro.name}.")

# ==============================================================================
# 🚀 INICIALIZAÇÃO
# ==============================================================================

@bot.event
async def on_ready():
    print(f"✅ Logado como {bot.user} (ID: {bot.user.id})")
    
    # Inicia as tarefas em loop
    if not check_giveaways.is_running():
        check_giveaways.start()
        
    # Sincroniza os comandos com o Discord
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Sincronizados {len(synced)} comandos slash.")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")

    await bot.change_presence(activity=discord.Game(name="Gerenciando o Servidor 🌙"))

# Inicia o servidor web
