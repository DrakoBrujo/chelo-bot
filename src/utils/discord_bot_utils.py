import discord

async def send_current_track_info(ctx, current_track):
    if current_track:
        url, title, duration = current_track
        await ctx.send(f"🎵 Reproduciendo ahora: {title} - Duración: {duration // 60}:{duration % 60:02d} 🎵")
    else:
        await ctx.send("No hay nada reproduciéndose actualmente.")

async def send_playlist_info(ctx, queue):
    if not queue:
        await ctx.send("No hay canciones en la peylist")
        return

    total_duration = sum(track[2] for track in queue)
    info_lines = [f"{idx + 1}. {track[1]} - {track[2] // 60}:{track[2] % 60:02d}" for idx, track in enumerate(queue)]

    await ctx.send(f"Canciones en la peylist ({len(queue)}):\n" + "\n".join(info_lines))
    await ctx.send(f"Duración total restante: {total_duration // 60} minutos {total_duration % 60} segundos")
