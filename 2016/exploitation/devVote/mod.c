/*
Device Driver Stub
*/


#include <linux/module.h>    
#include <linux/kernel.h>    
#include <linux/init.h>     

#include <linux/fs.h>        
#include <linux/string.h>    

#include <linux/miscdevice.h>


#include <asm/uaccess.h>


#include <linux/crypto.h>
#include <linux/err.h>
#include <linux/scatterlist.h>


/*static const struct file_operations proc_file_ops = {
	.owner = THIS_MODULE,
	.open = root,
};*/


int doCheck = 0;
char * oldptr = NULL;
char oldval = 0;

//&buffer+sizeof(buffer)%240 must be in the same 0xff00 mask as &buffer+sizeof(buffer)
//hex(0x70+388%240) = 0x104
//hex(0x70+388) = 0x1f4
char buffer[256];


int hash(unsigned int start, unsigned int end) {
    unsigned int i, j, k;
    unsigned int sum = 0;
    for (i=start; i<end; i++) {
        for (j=start; j<end; j++) {
            sum += buffer[((unsigned int)(i+j)) % 256];
        }
    }
    return sum;
}
static ssize_t doRead(struct file* file, char* buf, size_t count, loff_t *ppos) {
    if (count<256)
        return -EINVAL;

    if (*ppos != 0)
        return 0;

    if (copy_to_user(buf, buffer, 256))
        return -EINVAL;

    *ppos = 256;

    return 256;
}



static ssize_t doWrite(struct file* file, char* buf, size_t count, loff_t *ppos) {

    //printk("Buffer is located at %p\n",&buffer[0]);
    //printk("oldptr is located at %p\n",&oldptr);
    //printk("doCheck is located at %p\n",&doCheck);
    unsigned int* ibuf = buf;
    if (count < sizeof(unsigned int))
        return -EINVAL;

    if (*ppos != 0)
        return -EINVAL;

    if (*ibuf == 0) {
        /*
        if (count < 256+sizeof(unsigned int))
            return 0;
        memcpy(buffer, &ibuf[1], 256);
        printk("[+] Ballot reset\n");
        return 256;
        */
    } else if (*ibuf == 1) {
        if (count < sizeof(unsigned int)*2)
            return 0;
        unsigned int offset = ibuf[1];
        buffer[offset & 0xff]++;
        printk("[+] Vote recorded\n");
        return count;
    } else if (*ibuf == 2) {
        if (count < sizeof(unsigned int)*4)
            return 0;
        if (ibuf[1] != 0x6f776e)
            return 0;
        if (oldptr != NULL) {
            //printk("[?] oldptr was %p\n",oldptr);
            *oldptr = oldval;
            //printk("[?] writing %x to oldptr %p\n",oldval,oldptr);
            oldptr = NULL;
        }
        short offset = ibuf[2];
        oldptr = &buffer[offset];
        oldval = buffer[offset];
        //printk("[?] oldptr is now %p\n",oldptr);

        if (doCheck) {
            if (count < sizeof(unsigned int)*7)
                return 0;
            unsigned int sum = hash(ibuf[4], ibuf[5]);
            if (sum != ibuf[6]) {
                printk("[!] Consistency Check FAILED!\n");
                //printk("[?] Expected %x, got %x\n",sum, ibuf[6]);
                return 0;
            }
        }

       // printk("[?] Before %08x\n",*(unsigned int*)&buffer[offset]);
        buffer[offset] = (char)ibuf[3];
        //printk("[?] After %08x\n",*(unsigned int*)&buffer[offset]);
        printk("[+] Vote recorded\n");
        return count;
    }
    return 0;
}

static const struct file_operations ops = {
    .owner = THIS_MODULE,
    .write = doWrite,
    .read = doRead
};

static struct miscdevice votedev = {
        MISC_DYNAMIC_MINOR, "vote" , &ops
};

static int __init mod_init(void)
{
    misc_register(&votedev);

    memset(buffer, 0, 256);

    printk(KERN_INFO "[+] Vote-O-Matic Module Loaded \n");
    return 0;    
}

static void __exit mod_cleanup(void)
{
    printk(KERN_INFO "[+] Cleaning up module.\n");
}


module_init(mod_init);
module_exit(mod_cleanup);
