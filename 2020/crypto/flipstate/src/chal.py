#!/usr/bin/python3
import ast
import operator as op
import secrets

from multiprocessing import Process, Queue



operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.LShift: op.lshift,
    ast.RShift: op.rshift,
    ast.BitOr: op.or_,
    ast.BitXor: op.xor,
    ast.BitAnd: op.and_,
    ast.FloorDiv: op.floordiv,
    ast.UAdd: op.pos,
    ast.USub: op.neg,
    ast.Not: op.is_not,
    ast.Invert: op.not_,
}


def eval_expr(expr, ctx):
    return eval_(ast.parse(expr, mode="eval").body, ctx)


def eval_(node, ctx):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](eval_(node.left, ctx), eval_(node.right, ctx))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](eval_(node.operand, ctx))
    elif isinstance(node, ast.Name):
        if node.id == "literal":
            raise ValueError(node)
        return ctx[node.id]
    elif isinstance(node, ast.Subscript):
        if node.value.id != "literal":
            raise ValueError(node)
        if not isinstance(node.slice, ast.Index):
            raise ValueError(node)
        index = eval_(node.slice.value, ctx)
        if not isinstance(index, int):
            raise ValueError(node)
        return ctx["literal"][index]
    else:
        raise TypeError(node)

def encrypt_func(expr, literal, in_q, out_q):
    literal = ast.literal_eval(literal)

    while True:
        exited, random, vote = in_q.get()

        if exited:
            return

        bitflip = eval_expr(expr, {
            "random": random,
            "vote": vote,
            "literal": literal}
        )
        out_q.put(bitflip)

def decrypt_func(expr, literal, in_q, out_q):
    literal = ast.literal_eval(literal)

    while True:
        exited, encrypted_vote = in_q.get()

        if exited:
            return

        original_vote = eval_expr(expr, {
            "encrypted_vote": encrypted_vote,
            "literal": literal}
        )
        out_q.put(original_vote)


def score(literal, encrypt, decrypt):
    enc_in_q = Queue()
    enc_out_q = Queue()
    dec_in_q = Queue()
    dec_out_q = Queue()

    encrypt_proc = Process(
            target=encrypt_func,
            args=(encrypt, literal, enc_in_q, enc_out_q)
    )
    encrypt_proc.start()

    decrypt_proc = Process(
            target=decrypt_func,
            args=(decrypt, literal, dec_in_q, dec_out_q)
    )
    decrypt_proc.start()

    for x in range(20000):
        random = secrets.randbits(64) 
        vote = secrets.randbelow(64)

        enc_in_q.put((False, random, vote))
        bitflip = enc_out_q.get()

        encrypted_vote = random ^ (1 << (bitflip % 64))

        dec_in_q.put((False, encrypted_vote))
        recovered_vote = dec_out_q.get()

        if recovered_vote != vote:
            enc_in_q.put((True, None, None))
            dec_in_q.put((True, None))
            encrypt_proc.join()
            decrypt_proc.join()
            return False
        if x % 1000 == 0:
            print(f'{x}/20000')

    enc_in_q.put((True, None, None))
    dec_in_q.put((True, None))
    encrypt_proc.join()
    decrypt_proc.join()
    return True

print('''=== ELECTION COMMISSION GRANT SUBMISSION SERVER ===
Welcome! To apply for this grant you must show us your new vote encryption scheme.

Here is how it works:
- You will give us two expressions to evaluate: One for encryption and one for decryption
- For the encryption:
  o We will give you a random 64 bit number as `random` and a vote from 0-63 as `vote`
  o You must give us back the index of a bit to flip in that 64 bit random number (0-63)
  o We will flip that bit in the original random number to get the encrypted value

- For the decryption:
  o We will give you the encrypted vote as `encrypted_vote`
  o You must return the original vote
- You are allowed one constant literal to use for both encryption and decryption
- The encryption and decryption will be done separately so you cannot share information between them

We will test your crypto system 20000 times before we approve it.

Sound good? Alright lets get started!
''')

print('Enter a constant literal: (ie `[1,2,3,4]`):')
literal = input()
if len(literal) > 5000:
    print('Literal too long')
    exit(1)

print('Enter expression for vote encryption (ie `vote+100`).\nYour inputs are `random`, `vote`, and `literal`: ')
encrypt = input()
if len(encrypt) > 10000:
    print('Encrypt expression too long')
    exit(1)

print('Enter expression for vote decryption (ie `encrypted_vote*2`).\nYour inputs are `encrypted_vote`, and `literal`: ')
decrypt = input()
if len(decrypt) > 10000:
    print('Decrypt expression too long')
    exit(1)

if score(literal, encrypt, decrypt):
    with open('flag.txt') as f:
        print(f.read())
else:
    print('Sorry your system did not stand up to testing. Please feel free to reapply in the future!')
