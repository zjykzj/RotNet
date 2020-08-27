# -*- coding: utf-8 -*-

"""
@date: 2020/8/21 下午8:00
@file: trainer.py
@author: zj
@description: 
"""

import datetime
import time
import torch

from .inference import do_evaluation
from rotnet.util.metrics import topk_accuracy
from rotnet.util.metric_logger import MetricLogger


def do_train(cfg, arguments,
             data_loader, model, criterion, optimizer, lr_scheduler, checkpointer,
             device, logger):
    logger.info("Start training ...")
    meters = MetricLogger()

    model.train()

    start_iter = arguments['iteration']
    max_iter = len(data_loader)
    log_step = cfg.TRAIN.LOG_STEP
    save_step = cfg.TRAIN.SAVE_STEP
    eval_step = cfg.TRAIN.EVAL_STEP

    start_training_time = time.time()
    end = time.time()
    for iteration, (images, targets) in enumerate(data_loader, start_iter):
        iteration = iteration + 1
        arguments["iteration"] = iteration

        images = images.to(device)
        targets = targets.to(device)

        outputs = model(images)
        loss = criterion(outputs, targets)
        topk_list = topk_accuracy(outputs, targets, topk=(1,))
        meters.update(loss=loss / len(targets), acc=topk_list[0])

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        lr_scheduler.step()

        batch_time = time.time() - end
        end = time.time()
        meters.update(time=batch_time)
        if iteration % log_step == 0:
            eta_seconds = meters.time.global_avg * (max_iter - iteration)
            eta_string = str(datetime.timedelta(seconds=int(eta_seconds)))
            logger.info(
                meters.delimiter.join([
                    "iter: {iter:06d}",
                    "lr: {lr:.5f}",
                    '{meters}',
                    "eta: {eta}",
                    'mem: {mem}M',
                ]).format(
                    iter=iteration,
                    lr=optimizer.param_groups[0]['lr'],
                    meters=str(meters),
                    eta=eta_string,
                    mem=round(torch.cuda.max_memory_allocated() / 1024.0 / 1024.0),
                )
            )

        if iteration % save_step == 0:
            checkpointer.save("model_{:06d}".format(iteration), **arguments)
        if eval_step > 0 and iteration % eval_step == 0 and not iteration == max_iter:
            do_evaluation(cfg, model, device)
            model.train()  # *IMPORTANT*: change to train mode after eval.

    checkpointer.save("model_final", **arguments)
    # compute training time
    total_training_time = int(time.time() - start_training_time)
    total_time_str = str(datetime.timedelta(seconds=total_training_time))
    logger.info("Total training time: {} ({:.4f} s / it)".format(total_time_str, total_training_time / max_iter))
    return model