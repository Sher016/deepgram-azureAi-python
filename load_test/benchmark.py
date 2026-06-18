import asyncio
import aiohttp
import time
import argparse
import csv
import os
from typing import Tuple
from tqdm.asyncio import tqdm

from dotenv import load_dotenv
load_dotenv("../infra/.env")

BASE_URL = "http://localhost:8001"
TOTAL_REQUESTS = 1000
CONCURRENCY = 100

async def fetch_normal_stt(session: aiohttp.ClientSession, audio_bytes: bytes) -> Tuple[int, float]:
    start = time.time()
    data = aiohttp.FormData()
    data.add_field('file', audio_bytes, filename='test.mp3', content_type='audio/mpeg')
    try:
        async with session.post(f"{BASE_URL}/stt", data=data) as response:
            await response.read()
            status = response.status
    except Exception as e:
        status = 0
    return status, time.time() - start

async def fetch_better_way_stt(session: aiohttp.ClientSession, audio_bytes: bytes) -> Tuple[int, float]:
    start = time.time()
    data = aiohttp.FormData()
    data.add_field('file', audio_bytes, filename='test.mp3', content_type='audio/mpeg')
    try:
        async with session.post(f"{BASE_URL}/stt/better_way", data=data) as response:
            res_json = await response.json()
            task_id = res_json.get("task_id")
            if response.status != 200 or not task_id:
                return response.status, time.time() - start

        # Polling del resultado
        while True:
            async with session.get(f"{BASE_URL}/stt/result/{task_id}") as res_response:
                if res_response.status == 200:
                    await res_response.read()
                    status = res_response.status
                    break
                elif res_response.status == 202:
                    # Tarea aún procesando
                    await asyncio.sleep(0.5)
                else:
                    status = res_response.status
                    break
    except Exception as e:
        status = 0
    return status, time.time() - start

async def worker_normal(name: str, queue: asyncio.Queue, session: aiohttp.ClientSession, audio_bytes: bytes, results: list):
    while True:
        try:
            task = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        status, duration = await fetch_normal_stt(session, audio_bytes)
        results.append((status, duration))
        queue.task_done()

async def worker_better_way(name: str, queue: asyncio.Queue, session: aiohttp.ClientSession, audio_bytes: bytes, results: list):
    while True:
        try:
            task = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        status, duration = await fetch_better_way_stt(session, audio_bytes)
        results.append((status, duration))
        queue.task_done()

async def run_benchmark(endpoint_type: str, total_requests: int, concurrency: int):
    audio_bytes = b"dummy_audio_content"
    
    queue = asyncio.Queue()
    for i in range(total_requests):
        queue.put_nowait(i)
        
    results = []
    
    timeout = aiohttp.ClientTimeout(total=130)
    conn = aiohttp.TCPConnector(limit=concurrency)
    
    async with aiohttp.ClientSession(connector=conn, timeout=timeout, headers={"x-api-key": os.getenv("API_KEY")}) as session:
        workers = []
        start_time = time.time()
        for i in range(concurrency):
            if endpoint_type == "normal":
                task = asyncio.create_task(worker_normal(f"worker-{i}", queue, session, audio_bytes, results))
            else:
                task = asyncio.create_task(worker_better_way(f"worker-{i}", queue, session, audio_bytes, results))
            workers.append(task)
            
        await tqdm.gather(*workers)
        total_time = time.time() - start_time
        
    success = sum(1 for status, _ in results if status == 200)
    failed = len(results) - success
    avg_latency = sum(dur for _, dur in results) / len(results) if results else 0
    
    print(f"\n--- Resultados para endpoint '{endpoint_type}' ---")
    print(f"Peticiones totales: {total_requests}")
    print(f"Concurrencia:       {concurrency}")
    print(f"Tiempo total:       {total_time:.2f} segundos")
    print(f"Completadas (200):  {success}")
    print(f"Fallidas (Otras):   {failed}")
    print(f"Latencia promedio:  {avg_latency:.2f} segundos")
    print("--------------------------------------------------\n")

    return {
        "endpoint_type": endpoint_type,
        "total_requests": total_requests,
        "concurrency": concurrency,
        "total_time": round(total_time, 2),
        "success": success,
        "failed": failed,
        "avg_latency": round(avg_latency, 2)
    }

def save_to_csv(results_list, filename="load_test/benchmark_results.csv"):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as csvfile:
        fieldnames = ["endpoint_type", "total_requests", "concurrency", "total_time", "success", "failed", "avg_latency"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
            
        for result in results_list:
            writer.writerow(result)
    print(f"Resultados guardados en {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["normal", "better_way", "both"], default="both")
    parser.add_argument("--requests", type=int, default=1000)
    parser.add_argument("--concurrency", type=int, default=100)
    
    args = parser.parse_args()
    
    all_results = []
    
    if args.type in ["normal", "both"]:
        print("Corriendo prueba normal")
        res_normal = asyncio.run(run_benchmark("normal", args.requests, args.concurrency))
        all_results.append(res_normal)

    if args.type in ["better_way", "both"]:
        print("Corriendo prueba better way")
        res_better = asyncio.run(run_benchmark("better_way", args.requests, args.concurrency))
        all_results.append(res_better)
        
    if all_results:
        save_to_csv(all_results)
