"""
Caching library -- allows us to control granularity of multiprocessing across library
This allows us to abstract multiprocessing in a way that allows different-sized machines to work
with the same services.
"""


from multiprocessing import Pool, cpu_count


NUM_PROCESSES = 4
DEFAULT_POOL = None


def set_global_num_processes(num_processes):
    """
    Allows us to set a maximum number on processes per pool

    :param num_processes: max number of processes (default is 4)
    :type num_processes: int
    """
    global NUM_PROCESSES, DEFAULT_POOL
    NUM_PROCESSES = num_processes
    DEFAULT_POOL = Pool(processes=num_processes)


def pool(num_processes=None, with_max=False):
    """
    Retrieves a multiprocessing pool from module

    :param num_processes: a predefined set of processes, outside of global value set
    :type num_processes: int|None
    :param with_max: Whether to just use maximum number of CPUs
    :type with_max: bool

    :return: a multiprocessing pool
    :rtype: multiprocessing.pool.Pool

    """
    global DEFAULT_POOL, NUM_PROCESSES
    if with_max:
        num_processes = cpu_count()
    if num_processes is None or num_processes == NUM_PROCESSES:
        if not DEFAULT_POOL:
            DEFAULT_POOL = Pool(processes=num_processes)
        return DEFAULT_POOL
    return Pool(processes=num_processes)
