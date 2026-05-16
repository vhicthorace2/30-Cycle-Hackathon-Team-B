'use client';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowLeft, House, WarningCircle } from '@phosphor-icons/react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#FDFCF8] flex items-center justify-center p-6 selection:bg-[#00FF85] selection:text-black relative overflow-hidden">
      {/* Background Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[10%] left-[5%] w-64 h-64 bg-[#006D32]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-[10%] right-[5%] w-96 h-96 bg-[#00FF85]/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-2xl w-full relative z-10 text-center">
        {/* Modern 404 Container */}
        <div className="relative mb-8 inline-block">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ 
              type: "spring",
              stiffness: 260,
              damping: 20,
              delay: 0.1 
            }}
            className="text-[160px] md:text-[220px] font-black text-[#0B1C30] leading-none tracking-tighter"
            style={{ fontFamily: "'Space Grotesk', sans-serif" }}
          >
            404
          </motion.div>
          
          {/* Floating Badge */}
          <motion.div
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -top-4 -right-8 md:-right-12 bg-[#00FF85] border-2 border-black px-4 py-2 rounded-xl rotate-12 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center gap-2"
          >
            <WarningCircle size={24} weight="fill" className="text-black" />
            <span className="font-bold text-black uppercase text-sm tracking-wider">Lost in space?</span>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 
            className="text-4xl md:text-5xl font-black text-[#0B1C30] mb-6 tracking-tight uppercase" 
            style={{ fontFamily: "'Space Grotesk', sans-serif" }}
          >
            Whoops! Wrong Turn.
          </h2>

          <p className="text-[#4B5563] text-xl mb-12 max-w-md mx-auto leading-relaxed">
            The coordinate you requested doesn't exist in our creator universe. 
            Maybe it was never here, or it's been moved to another dimension.
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center px-4">
            <Link href="/" className="w-full sm:w-auto">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full sm:w-auto flex items-center justify-center gap-3 px-10 py-5 bg-[#006D32] text-white font-bold rounded-2xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] border-2 border-black hover:bg-[#005227] transition-all text-lg"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
              >
                <House size={28} weight="bold" />
                <span>BACK TO BASE</span>
              </motion.button>
            </Link>

            <Link href="/dashboard" className="w-full sm:w-auto">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full sm:w-auto flex items-center justify-center gap-3 px-10 py-5 bg-white text-[#0B1C30] font-bold rounded-2xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] border-2 border-black hover:bg-[#F3F4F6] transition-all text-lg"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
              >
                <ArrowLeft size={28} weight="bold" />
                <span>GO TO DASHBOARD</span>
              </motion.button>
            </Link>
          </div>
        </motion.div>

        {/* Footnote */}
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-20 text-sm font-bold text-[#9CA3AF] uppercase tracking-[0.2em]"
        >
          CIAP Influence Intelligence · Error Code: 404_NULL_REFERENCE
        </motion.p>
      </div>
    </div>
  );
}