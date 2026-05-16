CREATE TABLE "scouted_creators" (
	"id" serial PRIMARY KEY NOT NULL,
	"sme_id" integer NOT NULL,
	"creator_id" integer NOT NULL,
	"status" text DEFAULT 'scouted' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "reset_token" text;--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "reset_token_expires" timestamp with time zone;--> statement-breakpoint
ALTER TABLE "scouted_creators" ADD CONSTRAINT "scouted_creators_sme_id_users_id_fk" FOREIGN KEY ("sme_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "scouted_creators" ADD CONSTRAINT "scouted_creators_creator_id_users_id_fk" FOREIGN KEY ("creator_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "scouted_creators_sme_id_idx" ON "scouted_creators" USING btree ("sme_id");--> statement-breakpoint
CREATE INDEX "scouted_creators_creator_id_idx" ON "scouted_creators" USING btree ("creator_id");--> statement-breakpoint
CREATE UNIQUE INDEX "scouted_creators_uq" ON "scouted_creators" USING btree ("sme_id","creator_id");