from sta import StarGAN_v2
import argparse
from utils2 import *
import threading
import kthread
def parse_args(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,aa,bb,cc,dd,ee,ff,gg):
    desc = "gansta"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--phase', type=str, default=x, help='train or test or refer_test ?')
    parser.add_argument('--dataset', type=str, default=g, help='dataset_name')
    parser.add_argument('--refer_img_path', type=str, default='refer_img.jpg', help='reference image path')
    parser.add_argument('--iteration', type=int, default=r, help='The number of training iterations')
    parser.add_argument('--batch_size', type=int, default=c, help='The size of batch size') 
    parser.add_argument('--print_freq', type=int, default=y, help='The number of image_print_freq')
    parser.add_argument('--save_freq', type=int, default=dd, help='The number of ckpt_save_freq')
    parser.add_argument('--gpu_num', type=int, default=2, help='The number of gpu')
    parser.add_argument('--decay_flag', type=str2bool, default=h, help='The decay_flag')
    parser.add_argument('--decay_iter', type=int, default=i, help='decay start iteration')
    parser.add_argument('--lr', type=float, default=t, help='The learning rate')
    parser.add_argument('--ema_decay', type=float, default=k, help='ema decay value')
    parser.add_argument('--adv_weight', type=float, default=a, help='The weight of Adversarial loss')
    parser.add_argument('--sty_weight', type=float, default=ff, help='The weight of Style reconstruction loss') 
    parser.add_argument('--ds_weight', type=float, default=j, help='The weight of style diversification loss') 
    parser.add_argument('--cyc_weight', type=float, default=f, help='The weight of Cycle-consistency loss') 
    parser.add_argument('--r1_weight', type=float, default=z, help='The weight of R1 regularization')
    parser.add_argument('--gp_weight', type=float, default=m, help='The gradient penalty lambda')
    parser.add_argument('--gan_type', type=str, default=l, help='gan / lsgan / hinge / wgan-gp / wgan-lp / dragan')
    parser.add_argument('--sn', type=str2bool, default=ee, help='using spectral norm')
    parser.add_argument('--ch', type=int, default=d, help='base channel number per layer')
    parser.add_argument('--n_layer', type=int, default=v, help='The number of resblock')
    parser.add_argument('--n_critic', type=int, default=u, help='number of D updates per each G update')
    parser.add_argument('--style_dim', type=int, default=gg, help='length of style code')
    parser.add_argument('--num_style', type=int, default=w, help='number of styles to sample')
    parser.add_argument('--img_height', type=int, default=p, help='The height size of image')
    parser.add_argument('--img_width', type=int, default=q, help='The width size of image ')
    parser.add_argument('--img_ch', type=int, default=o, help='The size of image channel')
    parser.add_argument('--augment_flag', type=str2bool, default=b, help='Image augmentation use or not')
    parser.add_argument('--checkpoint_dir', type=str, default=e,
                        help='Directory name to save the checkpoints')
    parser.add_argument('--result_dir', type=str, default=bb,
                        help='Directory name to save the generated images')
    parser.add_argument('--log_dir', type=str, default=s,
                        help='Directory name to save training logs')
    parser.add_argument('--sample_dir', type=str, default=cc,
                        help='Directory name to save the samples on training')
    return check_args(parser.parse_args())
def check_args(args):
    check_folder(args.checkpoint_dir)
    check_folder(args.result_dir)
    check_folder(args.log_dir)
    check_folder(args.sample_dir)
    try:
        assert args.epoch >= 1
    except:
        print('number of epochs must be larger than or equal to one')
    try:
        assert args.batch_size >= 1
    except:
        print('batch size must be larger than or equal to one')
    return args
def action(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,aa,bb,cc,dd,ee,ff,gg):
    args = parse_args(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,aa,bb,cc,dd,ee,ff,gg)
    print("************************************************* our arguments:  " + str(args))
    with tf.Session(config=tf.ConfigProto(allow_soft_placement=True, gpu_options=tf.GPUOptions(allow_growth=True,  per_process_gpu_memory_fraction=0.8))) as sess:
        gan = StarGAN_v2(sess, args)
        gan.build_model()
        show_all_variables()
        if args.phase == 'train' :
            gan.train()
            print(" [*] Training finished!")
        elif args.phase == 'refer_test' :
            gan.refer_test()
            print(" [*] Refer test finished!")
        else :
            gan.test()
            print(" [*] Test finished!")
def xx(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,aa,bb,cc,dd,ee,ff,gg):
    x = kthread.KThread(target=action, args=(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,aa,bb,cc,dd,ee,ff,gg))
    x.start()
    return x
